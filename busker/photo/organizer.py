import sqlite3
import tkinter as tk
import os
import shutil
import logging
import traceback
from gettext import gettext as _
from tkinter import filedialog, messagebox
from busker.tkinter import center_window, MessagePanel
from busker.utils import init_i18n, init_logging
from busker.photo.file_info import read_all_files
from busker.photo import sql


# init_logging('photo_organizer.log', logging.INFO, 'utf-8')
logger = logging.getLogger("busker.photo.organizer")
logger.setLevel(logging.INFO)


class PhotoOrganizer:
    """写真整理プログラム"""

    batch_size = 100        # 一回にて処理できるファイルの数

    def __init__(self, conn):
        self.conn = conn
        # テーブル定義
        sql.create_table_file_info(conn)

        self.window = tk.Tk()
        self.window.title(_("Collect Photos Automatically"))        # noqa F821
        self.window_width = 400
        self.window_height = 600
        center_window(self.window, offsetx=100, offsety=200)

        # Source directory
        row = 0
        self.src_label = tk.Label(self.window, text=_("Source Directory"))      # noqa F821
        self.src_label.grid(row=row, column=0, padx=10, pady=10)
        
        self.src_entry = tk.Entry(self.window, width=50, state='readonly')
        self.src_entry.grid(row=row, column=1, padx=10, pady=10)
        
        self.src_button = tk.Button(self.window, text=_("Select"), command=self.select_source_directory)    # noqa F821
        self.src_button.grid(row=row, column=2, pady=10)

        # Target directory
        row += 1
        self.tgt_label = tk.Label(self.window, text=_("Target Directory"))      # noqa F821
        self.tgt_label.grid(row=row, column=0, padx=10, pady=10)
        
        self.tgt_entry = tk.Entry(self.window, width=50, state=tk.DISABLED)
        self.tgt_entry.grid(row=row, column=1, padx=10, pady=10)
        
        self.tgt_button = tk.Button(self.window, text=_("Select"), command=self.select_target_directory)    # noqa F821
        self.tgt_button.grid(row=row, column=2, pady=10)

        # message panel
        row += 1
        self.message_panel = MessagePanel(42, 30, master=self.window, max_lines=50)
        self.message_panel.grid(row=row, column=0, columnspan=2, pady=10, sticky='e')

        # buttons
        row += 1
        self.collect_button = tk.Button(self.window, text=_("Collect photos"), command=self.collect_photos)   # noqa F821
        self.collect_button.grid(row=row, column=0, columnspan=2, pady=10, padx=(0, 20), sticky='e')

        # Close button at the third line
        self.close_button = tk.Button(self.window, text=_("Close"), command=self.on_closing)    # noqa F821
        self.close_button.grid(row=row, column=2, pady=10, padx=(0, 10))

        # Intercept the window close event(the 'X' button in the upper-right corner of the window)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if self.close_button['state'] == tk.NORMAL:  # Button is active
            result = messagebox.askokcancel(_("Quit"), _("Do you really want to quit?"))        # noqa F821
            if result:
                self.window.destroy()

    def select_source_directory(self):
        """整理元となるフォルダーを指定する"""

        folder_selected = filedialog.askdirectory()
        self.src_entry.config(state=tk.NORMAL)
        self.src_entry.delete(0, tk.END)
        self.src_entry.insert(0, folder_selected.replace('/', os.path.sep))
        self.src_entry.config(state=tk.DISABLED)

    def select_target_directory(self):
        """バックアップ先フォルダーを指定する"""

        folder_selected = filedialog.askdirectory()
        self.tgt_entry.config(state=tk.NORMAL)
        self.tgt_entry.delete(0, tk.END)
        self.tgt_entry.insert(0, folder_selected.replace('/', os.path.sep))
        # self.tgt_entry.config(state='readonly')

    def collect_photos(self):
        """写真を元の場所から保存先へコピーする、コピーした写真情報はDBに収集保存する"""

        if not self.src_entry.get():
            messagebox.showerror(_("Input Error"), _("Input Required"), _("{} must be entered.").format(self.src_label.cget("text")))     # noqa F821
            return

        target_folder = self.tgt_entry.get()
        if not target_folder:
            messagebox.showerror(_("Input Error"), _("Input Required"), _("{} must be entered.").format(self.tgt_label.cget("text")))     # noqa F821
            return
        
        if os.path.exists(target_folder):
            if any(os.listdir(target_folder)):
                result = messagebox.askyesno(_("Confirmation"), _("The destination folder is not empty. Do you want to proceed?"))      # noqa F821
                if not result:
                    return
        else:
                result = messagebox.askyesno(_("Confirmation"), _("The destination folder is not exist. Do you want to create it?"))      # noqa F821
                if not result:
                    return

        try:
            self.close_button.config(state=tk.DISABLED)
            self.close_button.update()
            self.message_panel.text_widget.config(state=tk.NORMAL)
            self.message_panel.text_widget.update()

            # 保存先フォルダーにあるファイルの情報がDBに未登録の場合は追加登録する
            self.inspect_collected_files(self.tgt_entry.get())

            self.message_panel.add_message(_('Copying and collecting photos...'))        # noqa F821
            logger.info('Copying and collecting photos...')

            # 写真を元の場所から保存先にコピーし、DBにファイル情報を登録する
            self.copy_photos(self.src_entry.get(), self.tgt_entry.get())

            self.message_panel.add_message(_('Coping and collecting photos has finished.'))      # noqa F821
            self.message_panel.text_widget.config(state=tk.DISABLED)
            logger.info('Coping and collecting photos has finished.')
            self.close_button.config(state=tk.NORMAL)
        except Exception as e:
            logger.error(f"An unknown error occurred: {e}\n{traceback.format_exc()}")
            print(f"An unknown error occurred: {e}\n{traceback.format_exc()}")
            messagebox.showerror(_("Unknown Error"), "System error happened, we will close the window.")     # noqa F821
            self.window.destroy()

    def inspect_collected_files(self, target_path: str) -> None:
        """保存先フォルダーにあるファイル情報が未収集の場合、DBに追加収集する"""

        self.message_panel.add_message(_('Collecting photo information...'))        # noqa F821
        logger.info('Collecting photo information...')

        for file_infos in read_all_files(target_path, 1000):
            for file_info in file_infos:
                save_to = file_info.get_relative_path(target_path)
                # ファイルがすでに収集済みかをチェックする、収集済みの場合は特に処理なし
                if not sql.get_file_by_save_to__name(self.conn, save_to, file_info.name):
                    # 未収集の場合、ファイルの名称、サイズとMD5で同一ファイルが既に収集済みかをチェックする
                    existing = sql.get_same_file(self.conn, file_info)
                    if existing:    # 同一ファイルが既に収集済の場合は特に処理なし
                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logger.debug(f'Picture[{existing.full_name}] info already exists, the file {file_info.full_name} will not be collected.')     # noqa
                    else:           # 同ファイルが未収集の場合、追加収集する
                        file_info.save_to = save_to
                        sql.register_file_info(self.conn, file_info)
                        logger.debug(f'File {file_info.full_name} has been added to the database.')     # noqa

        self.message_panel.add_message(_('Collecting photo information has finished.'))        # noqa F821
        logger.info('Collecting photo information has finished.')

    def copy_photos(self, source_path: str, target_path: str) -> None:
        """指定フォルダー下にある写真ファイルを保存先にコピーし、ファイル情報をDBに収集する"""
        current_path = ''
        for file_infos in read_all_files(source_path, 500):
            for file_info in file_infos:
                # 現在処理中のフォルダー名を画面表示する
                if current_path != file_info.path:
                    current_path = file_info.path
                    self.message_panel.add_message(f'{current_path}')        # noqa F821
                    logger.info(f'Collecting files from directory {current_path}.')

                # ファイルの名称、サイズとMD5で同一ファイルが既に収集済みかをチェックする
                existing = sql.get_same_file(self.conn, file_info)
                if existing:    # 同一ファイルが既に収集済の場合は特に処理なし
                    logger.debug(f'Picture[{existing.full_name}] already exists, the file {file_info.full_name} will not be copied.')     # noqa
                else:           # 同ファイルが未収集の場合、追加収集する
                    target_folder = os.path.join(target_path, file_info.save_to)
                    # 保存先フォルダーに年・月ごとにサブフォルダーを作成する
                    os.makedirs(target_folder, exist_ok=True)
                    original_file = file_info.full_name

                    count = 0
                    # ファイル名重複チェック
                    file_name = file_info.name
                    while sql.get_file_by_save_to__name(self.conn, file_info.save_to, file_name):
                        # ファイル名の重複がなくなるまでループする
                        count += 1
                        base, extension = os.path.splitext(file_info.name)
                        file_name = base + '_' + str(count).zfill(2) + extension

                    # 写真を保存先へコピー
                    shutil.copy2(original_file, os.path.join(target_folder, file_name))

                    # ファイル情報の収集
                    file_info.name = file_name
                    sql.register_file_info(self.conn, file_info)
                    logger.info(f'\tFile {original_file} has been copied to {os.path.join(target_folder, file_name)}.')
            self.conn.commit()

    def run(self):
        self.window.mainloop()


with sqlite3.connect('photo_organizer.db') as connection:
    init_logging('photo_organizer.log', logging.INFO, 'utf-8')
    localedir = os.path.join(os.path.dirname(__file__), 'locale')
    init_i18n('busker', localedir, 'ja_JP')
    app = PhotoOrganizer(connection)
    app.run()

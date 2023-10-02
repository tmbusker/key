import sqlite3
import tkinter as tk
import os
import shutil
from tkinter import filedialog, messagebox
from datetime import datetime
from typing import Any
from busker.tkinter.utils import center_window, MessagePanel
from busker.file.utils import init_i18n, init_logging, FileType, get_image_capture_datetime, \
     calculate_md5, read_all_files
from busker.file import sql
import logging
import traceback


# init_logging('file_organizer.log', logging.INFO, 'utf-8')
logger = logging.getLogger("busker.backupper")
logger.setLevel(logging.INFO)


class Backupper:
    batch_size = 100

    def __init__(self, conn):
        self.conn = conn
        # テーブル定義
        sql.create_table_file_info(conn)

        self.window = tk.Tk()
        self.window.title("Collect files Automatically")
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
        self.collect_button = tk.Button(self.window, text=_("Collect files"), command=self.collect_files)   # noqa F821
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
        folder_selected = filedialog.askdirectory()
        self.src_entry.config(state=tk.NORMAL)
        self.src_entry.delete(0, tk.END)
        self.src_entry.insert(0, folder_selected.replace('/', os.path.sep))
        self.src_entry.config(state=tk.DISABLED)

    def select_target_directory(self):
        folder_selected = filedialog.askdirectory()
        self.tgt_entry.config(state=tk.NORMAL)
        self.tgt_entry.delete(0, tk.END)
        self.tgt_entry.insert(0, os.path.join(folder_selected, 'backup_dir').replace('/', os.path.sep))
        self.tgt_entry.config(state='readonly')

    def collect_files(self):
        if not self.src_entry.get():
            messagebox.showerror(_("Input Required"), _("{} must be entered.").format(self.src_label.cget("text")))     # noqa F821
            return

        if not self.tgt_entry.get():
            messagebox.showerror(_("Input Required"), _("{} must be entered.").format(self.tgt_label.cget("text")))     # noqa F821
            return

        try:
            self.close_button.config(state=tk.DISABLED)
            self.close_button.update()
            self.message_panel.text_widget.config(state=tk.NORMAL)
            self.message_panel.text_widget.update()

            # 保存先フォルダーにあるファイルの情報がDBに未登録の場合は追加登録する
            if not sql.get_count(self.conn):
                self.message_panel.add_message(_('Collecting file information...'))        # noqa F821
                logger.info('Collecting file information...')
                self.inspect_collected_files(self.tgt_entry.get())

            self.message_panel.add_message(_('Copying and collecting files...'))        # noqa F821
            logger.info('Copying and collecting files...')

            # 写真を元の場所から保存先にコピーし、DBにファイル情報を登録する
            self.copy_files(self.src_entry.get(), self.tgt_entry.get())

            self.message_panel.add_message('Coping and collecting files has finished.')
            self.message_panel.text_widget.config(state=tk.DISABLED)
            logger.info('Coping and collecting files has finished.')
            self.close_button.config(state=tk.NORMAL)
        except Exception as e:
            logger.error(f"An unknown error occurred: {e}\n{traceback.format_exc()}")
            print(f"An unknown error occurred: {e}\n{traceback.format_exc()}")
            messagebox.showerror("System error happened, we will close the window.")     # noqa F821
            self.window.destroy()

    def inspect_collected_files(self, target_path: str) -> None:
        """保存先フォルダーにあるファイル情報が未収集の場合、DBに追加収集する"""
        for files in read_all_files(target_path, 1000):
            for file_path, file_name in files:
                relative_path = file_path.replace(target_path + os.path.sep, '')
                # ファイルがすでに収集済みかをチェックする、収集済みの場合は特に処理なし
                if not sql.get_file_by_relative_path_name(self.conn, relative_path, file_name):
                    file_info = self.get_file_info(file_path, file_name)
                    # 未収集の場合、ファイルの名称、サイズとMD5で同一ファイルが既に収集済みかをチェックする
                    existing = sql.get_same_file(self.conn, file_info)
                    if existing:    # 同一ファイルが既に収集済の場合は特に処理なし
                        current_file = os.path.join(file_path, file_name)
                        existing_file = os.path.join(existing['path'], existing['name'])
                        logger.info(f'Same picture[{existing_file}] already exists, the file {current_file} will not be collected.')     # noqa
                    else:           # 同ファイルが未収集の場合、追加収集する
                        file_info['relative_path'] = relative_path
                        sql.register_file_info(self.conn, file_info)
                        logger.info(f'File {os.path.join(file_path, file_name)} has been added to the database.')

    def copy_files(self, source_path: str, target_path: str) -> None:
        """指定フォルダー下にある写真ファイルを保存先にコピーし、ファイル情報をDBに収集する"""
        current_path = ''
        for files in read_all_files(source_path, 500):
            for file_path, file_name in files:
                current_file = os.path.join(file_path, file_name)
                file_info = self.get_file_info(file_path, file_name)

                # 現在処理中のフォルダー名を画面表示する
                if current_path != file_path:
                    current_path = file_path
                    self.message_panel.add_message(f'{current_path}')        # noqa F821
                    logger.info(f'Collecting files from directory {current_path}.')

                # ファイルの名称、サイズとMD5で同一ファイルが既に収集済みかをチェックする
                existing = sql.get_same_file(self.conn, file_info)
                if existing:    # 同一ファイルが既に収集済の場合は特に処理なし
                    existing_file = os.path.join(existing['path'], existing['name'])
                    logger.info(f'Same picture[{existing_file}] already exists, the file {current_file} will not be copied.')     # noqa
                else:           # 同ファイルが未収集の場合、追加収集する
                    relative_path = file_info['relative_path']
                    target_folder = os.path.join(target_path, relative_path)
                    # 保存先フォルダーに年・月ごとにサブフォルダーを作成する
                    os.makedirs(target_folder, exist_ok=True)

                    count = 0
                    # ファイル名重複チェック
                    while sql.get_file_by_relative_path_name(self.conn, relative_path, file_name):
                        # ファイル名の重複がなくなるまでループする
                        count += 1
                        base, extension = os.path.splitext(file_name)
                        file_name = base + '_' + str(count).zfill(2) + extension
                        file_info['name'] = file_name

                    # 写真を保存先へコピー
                    shutil.copy2(current_file, os.path.join(target_folder, file_name))

                    # ファイル情報の収集
                    sql.register_file_info(self.conn, file_info)
                    logger.info(f'File {current_file} has been copied to {target_folder}.')
            self.conn.commit()

    def run(self):
        self.window.mainloop()

    def get_file_info(self, file_path: str, file_name: str) -> dict[str, Any]:
        full_path = os.path.join(file_path, file_name)
        file_type = FileType.get_file_type(file_name)

        file_info: dict[str, Any] = {}
        file_info['path'] = file_path
        file_info['name'] = file_name
        file_info['size'] = os.path.getsize(full_path)
        file_info['file_type'] = file_type
        file_info['created_at'] = datetime.fromtimestamp(os.path.getctime(full_path))
        file_info['modified_at'] = datetime.fromtimestamp(os.path.getmtime(full_path))
        file_info['md5'] = calculate_md5(full_path)
        # 年・月ごとの相対パスをセットする
        file_info['relative_path'] = file_info['modified_at'].strftime('%Y' + os.path.sep + '%m')
        file_info['original_datetime'] = None

        if file_type == FileType.IMAGE:
            original_datetime = get_image_capture_datetime(full_path)
            if original_datetime:
                file_info['original_datetime'] = original_datetime
                file_info['relative_path'] = original_datetime[:7].replace(':', os.path.sep)

        return file_info


with sqlite3.connect('file_organizer.db') as connection:
    init_logging('file_organizer.log', logging.INFO, 'utf-8')
    localedir = os.path.join(os.path.dirname(__file__), 'locale')
    init_i18n('busker', localedir, 'ja_JP')
    app = Backupper(connection)
    app.run()

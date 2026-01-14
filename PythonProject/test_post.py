import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests


class FlexibleTempClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("灵活 Temp 服务测试客户端")
        self.root.geometry("500x380")
        self.root.resizable(False, False)

        # === 配置区域 ===
        config_frame = tk.LabelFrame(root, text="服务配置", padx=10, pady=10)
        config_frame.pack(fill="x", padx=15, pady=10)

        # URL 输入
        tk.Label(config_frame, text="服务地址:").grid(row=0, column=0, sticky="w", pady=3)
        self.url_entry = tk.Entry(config_frame, width=50)
        self.url_entry.insert(0, "http://localhost:5000/ypsl")
        self.url_entry.grid(row=0, column=1, padx=5, pady=3)

        # 参数键名输入
        tk.Label(config_frame, text="参数字段名:").grid(row=1, column=0, sticky="w", pady=3)
        self.param_key_entry = tk.Entry(config_frame, width=20)
        self.param_key_entry.insert(0, "ypxh")  # 默认值
        self.param_key_entry.grid(row=1, column=1, sticky="w", padx=5, pady=3)

        # === 查询区域 ===
        query_frame = tk.Frame(root)
        query_frame.pack(pady=5)

        tk.Label(query_frame, text="参数值:").pack(side=tk.LEFT)
        self.param_value_entry = tk.Entry(query_frame, width=30)
        self.param_value_entry.pack(side=tk.LEFT, padx=5)
        self.param_value_entry.focus()

        self.query_btn = ttk.Button(root, text="🔍 发送请求", command=self.on_query)
        self.query_btn.pack(pady=8)

        # === 结果区域 ===
        result_frame = tk.LabelFrame(root, text="响应结果", padx=10, pady=10)
        result_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.result_text = tk.Text(result_frame, height=8, state='disabled')
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        self.result_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # === 状态栏 ===
        self.status_var = tk.StringVar(value="就绪")
        status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, fg="gray")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def set_status(self, msg):
        self.status_var.set(msg)
        self.root.update_idletasks()

    def on_query(self):
        url = self.url_entry.get().strip()
        param_key = self.param_key_entry.get().strip()
        param_value = self.param_value_entry.get().strip()

        if not url:
            messagebox.showwarning("配置错误", "请输入服务地址！")
            return
        if not param_key:
            messagebox.showwarning("配置错误", "请输入参数字段名！")
            return
        if not param_value:
            messagebox.showwarning("输入错误", f"请输入 {param_key} 的值！")
            return

        # 启动后台线程
        threading.Thread(target=self.do_query, args=(url, param_key, param_value), daemon=True).start()

    def do_query(self, url, param_key, param_value):
        self.root.after(0, self.query_btn.config, {"state": "disabled"})
        self.set_status("正在发送请求...")

        try:
            payload = {param_key: param_value}
            response = requests.post(url, json=payload, timeout=10)

            # 尝试解析 JSON，失败则显示原始文本
            try:
                formatted = json.dumps(response.json(), indent=2, ensure_ascii=False)
            except:
                formatted = response.text

            status_line = f"状态码: {response.status_code}\n"
            result = status_line + "响应内容:\n" + formatted

        except requests.exceptions.ConnectionError:
            result = "❌ 连接失败\n请检查服务地址是否正确，或服务是否已启动。"
        except requests.exceptions.Timeout:
            result = "❌ 请求超时（10秒）"
        except requests.exceptions.RequestException as e:
            result = f"❌ 请求异常:\n{str(e)}"
        except Exception as e:
            result = f"❌ 未知错误:\n{str(e)}"

        # 安全更新 UI
        self.root.after(0, self.display_result, result)
        self.root.after(0, self.query_btn.config, {"state": "normal"})
        self.root.after(0, self.set_status, "就绪")

    def display_result(self, text):
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state='disabled')


if __name__ == '__main__':
    import json  # 确保 json 在作用域内
    root = tk.Tk()
    app = FlexibleTempClientGUI(root)
    root.mainloop()
from main import app


print("请输入文档内容：")
doc_content_lines = []
line = input()
doc_content_lines.append(line)


doc_content = "\n".join(doc_content_lines).strip()

# 构建输入数据
input_data = {
    "doc_title": "未命名文档",
    "doc_content": doc_content if doc_content else "",
}

if not doc_content:
    print("警告：文档内容为空！")

print("\n开始处理...")
result = app.invoke(input_data)
print("\n处理完成！")

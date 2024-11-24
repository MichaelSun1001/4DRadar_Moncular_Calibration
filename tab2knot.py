import csv

input_file = r"C:\Users\10137\Desktop\radar.txt"  # 输入文件路径
output_file = "output.csv"  # 输出文件路径

with open(input_file, "r") as infile, open(output_file, "w", newline='') as outfile:
    reader = csv.reader(infile, delimiter="\t")  # 指定 Tab 作为分隔符
    writer = csv.writer(outfile, delimiter=",")  # 输出为逗号分隔
    for row in reader:
        # 对数值进行格式化（保留6位小数）
        formatted_row = [
            "{:.6f}".format(float(value)) if value.replace('.', '', 1).lstrip('-').isdigit() else value 
            for value in row
        ]
        writer.writerow(formatted_row)

print(f"文件已转换为逗号分隔格式，并格式化小数，保存为 {output_file}")

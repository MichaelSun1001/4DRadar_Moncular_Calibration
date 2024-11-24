import xlrd
import numpy as np
import pandas as pd


worksheet = xlrd.open_workbook('0408.xlsx')
sheet_names= worksheet.sheet_names()
for sheet_name in sheet_names:
    sheet = worksheet.sheet_by_name(sheet_name)
    rows = sheet.nrows # 获取行数
    cols = sheet.ncols # 获取列数，尽管没用到
    all_content = []


    cols = sheet.col_values(4) # 获取第二列内容， 数据格式为此数据的原有格式（原：字符串，读取：字符串；  原：浮点数， 读取：浮点数）
    cols1 = sheet.col_values(5) # 获取第二列内容， 数据格式为此数据的原有格式（原：字符串，读取：字符串；  原：浮点数， 读取：浮点数）
    cols2 = sheet.col_values(6)
    cols3 = sheet.col_values(2)
    cols4 = sheet.col_values(1)




x = []
y = []
vx = []
fps = []
time_r = []
for index,i in enumerate(cols):
    x.append(float(cols[index]))
    y.append(float(cols1[index]))
    vx.append(float(cols2[index]))
    fps.append(float(cols3[index]))
    time_r.append(int(cols4[index]))

x1 = []
y1 = []
vx1 = []
fps1 = []
for index,i in enumerate(vx):
    if -5 < i < 5:
        x1.append(x[index])
        y1.append(y[index])
        vx1.append(vx[index])
        fps1.append(fps[index])

x2 = []
y2 = []
vx2 = []
fps2 = []

for index,i in enumerate(x1):
    if 1<= i < 10:
        x2.append(x1[index])
        y2.append(y1[index])
        vx2.append(vx1[index])
        fps2.append(fps1[index])
    else:
        continue

H = np.mat([[-1.58513926e+04 ,4.25153683e+04,-2.87902081e+02],[-6.80368904e+03,-1.45462749e+03,-5.89509358e+04],[-1.62517645e+01,-5.10463111e-01 ,1.00000000e+00]])

u = []
v = []
fps_img = []
for index, i in enumerate(x2):
    m = np.mat([[x2[index]], [y2[index]], [1]])
    n = H * m
    a = int(n[0][0] / n[2][0])
    b = int(n[1][0] / n[2][0])
    c = int(fps2[index] * 75 / 43)
    fps_img.append(c)
    u.append(a)
    v.append(b)

time = []
for index,i in enumerate(time_r):
    if (index+1) < len(time_r):
        a = (-time_r[index]) - (-time_r[index + 1])
        if a != 0:
            time.append(a)

#np.array([[fps_img],[u],[v]])
a = np.mat(fps_img).T
b = np.mat(u).T
c = np.mat(v).T

B = np.concatenate((a, b), axis=1) #列拼接
out = np.concatenate((B, c), axis=1) #数组拼接
out = np.array(out)

writer = pd.ExcelWriter('uv0408.xlsx')

array_1 = out
data_1 = pd.DataFrame(array_1)
# header参数表示列的名称，index表示行的标签
data_1.to_excel(writer, 'sheet_1', float_format='%.2f', header=None, index=False)
# 注意写多个的时候要把所有数据都给了writer后再调用save函数，要不然可能只有一个sheet
writer.save()
writer.close()
# m = 5
# for index,i in enumerate(time):
#     if index <= 26:
#         a+=time[index]
# print(a)









# np.array([[fps_img],[u],[v]])
#
# a = np.mat(fps_img).T



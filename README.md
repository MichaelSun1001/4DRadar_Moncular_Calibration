使用流程：
1、pixel_point_selector.py选取图片点
2、extract_incenter.py提取所有图片点的内心点
3、使用process_pointcloud_data.py、point_cloud_representative_calculator.py选取角反射器点云。
4、使用calibration.py、或calibration_test.py进行标定，得到外参矩阵
5、使用point_cloud_project_to_image .py进行点云的投影

遗留问题：
1、point_cloud_representative_calculator.py、process_pointcloud_data.py这两个代码只是用来处理点云数据的，处于测试阶段。




注意！！！

损失函数是**所有像素点和投影点误差的总和，而且图片分辨率越大损失函数越大，损失函数的单位是像素，没有做归一化处理。**

处理数据集的时候注意每个CSV中的格式以及图片的名称格式，要么改格式要么改程序。

# 原理资料与本例的简化

| 讲解点 | 资料 | 本例怎样表现 |
| --- | --- | --- |
| 磁铁在导电铜管中慢落，运动诱发涡流并产生阻碍运动的作用 | [Arizona State University](https://pirt.asu.edu/demos/5K20.25) | 完整管与开缝管使用相同重力、初态与尺寸，示意阻尼不同 |
| 贯通纵缝改变铜管环向导电条件 | [Swarthmore](https://demos.swarthmore.edu/physics/2015/06/lenzs-law-pipe/)、[William & Mary的Eddy Currents 2](https://physics.wm.edu/~labs/demo/elec.html) | 右侧真实纵缝与左侧完整回路并排；保留开缝后的剩余阻尼 |
| 铜并非铁磁材料；铜管可用连续环带理解，磁通变化诱发环向电流 | [MIT 6.013课程解答](https://ocw.mit.edu/courses/6-013-electromagnetics-and-applications-spring-2009/08b9c7c25b478f60fdec835d976b95ec_MIT6_013S09_sol_pset04.pdf) | 不声称铜毫无磁响应；固定观察一圈铜，电流方向随磁铁接近与远离变化 |
| 感应作用阻碍磁通变化；能量在铜的电阻中转为热 | [UW–Madison](https://www.physics.wisc.edu/ingersollmuseum/exhibits/EM/lenzlaw/) | 重力与电磁阻力方向相反，磁铁仍下落；能量图不夸大实际温升 |

位置相关线性阻尼、放慢时轴与理想软垫停止运动是动画模型，不是实测落时预测或完整电磁仿真。场线和环流为解释图形。完整铜管前壁仅透视；截面特写不改变下落实验条件。

本例参数与检查范围在[model.json](model.json)，动力学与能量计算在[source/model.js](source/model.js)。能量段位于磁铁接触软垫之前，不把软垫吸收的动能记成铜管发热。其他磁铁、管材、缝宽或几何需要重新核实，不能直接推广本例阻尼值。

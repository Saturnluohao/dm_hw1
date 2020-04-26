from method3.FTCTree import FTCTree
import method3.FTCTree as ftct

tree1 = FTCTree('tree1')
tree1.set('11')
tree1.set('22')
tree1.set('11')

tree2 = FTCTree('tree2')
tree2.set('11')
tree2.set('11')
tree2.set('22')

dis = ftct.get_dis(tree1, tree2)
print(dis)
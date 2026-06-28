import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
def round_preserve_sum_series(series, decimals=0):
    """
    对Pandas Series进行四舍五入并保持总和不变
    """
    # 初步四舍五入
    rounded = series.round(decimals)

    # 计算差异
    difference = round(series.sum(), decimals) - round(rounded.sum(), decimals)

    # 如果存在差异，调整数值
    if difference != 0:
        # 计算余数
        remainders = series - rounded

        # 找出余数最大的几个值进行调整
        adjustment = int(round(difference * (10 ** decimals)))
        to_adjust = remainders.abs().nlargest(abs(adjustment)).index

        # 应用调整
        for i in to_adjust:
            rounded[i] += np.sign(difference) * (10 ** -decimals)

    return rounded

#df=gpd.read_file(r'F:\HDY\202506河池油茶低改和单水肥\低改和单水肥数据库.gdb',layer='环江低改评审数据库')
#df=gpd.read_file(r'F:\HDY\202506河池油茶低改和单水肥\环江油茶0908修正.gdb',layer='环江低改和单水肥1014')
df=gpd.read_file(r'F:\HDY\202604河池油茶更新\环江毛南族自治县\环江低改v202605\环江低改交给设计5.14\环江低改数据整理v202605.shp')
df=df.loc[df.loc[:,"营林方式"].isin(['低改','低改+水肥']),:].reset_index(drop=True)
#df = df.loc[((df.loc[:,"bdyy"] != '删除9.24') & (df.loc[:,"bdyy"] != '删除9.25'))].reset_index(drop=True)
#df=df.loc[df.loc[:,"是否采用"]!='0617删',:].reset_index(drop=True)
#df = df.loc[((df.loc[:,"备注1"] != '0627删') & (df.loc[:,"是否采用"] != '0617删')) | (df.loc[:,"备注1"] == '0627回调')].reset_index(drop=True)

df.loc[:,"林分清理"]=df.loc[:,"作业面积"]*0.5*180
#df.loc[:,"密度调整"]=df.loc[:,"作业面积"]*1.6*180  #0827注释
df.loc[:,"整枝修剪"]=df.loc[:,"作业面积"]*1.5*180
df.loc[:,"垦复"]=df.loc[:,"作业面积"]*2.5*180
df.loc[df.loc[:,"营林方式"]=='低改',"施肥"]=df.loc[:,"作业面积"]*2*180
df.loc[df.loc[:,"营林方式"]=='低改+水肥',"施肥"]=df.loc[:,"作业面积"]*0.8*180
df.loc[:, "割灌除草"] =df.loc[:,"作业面积"]*1.4*180
df.loc[:,"全面铲草"]=df.loc[:,"作业面积"]*1.5*180
df.loc[:,"病虫害防控"]=df.loc[:,"作业面积"]*0.1*180

df.loc[:,"药剂费"]=df.loc[:,"作业面积"]*14.6
df.loc[:,"扩宽条带、修筑高水平梯带等其他费用"]=df.loc[:,"作业面积"]*931
df.loc[:,"坡度"]=df.loc[:,"坡度"].astype(float)
df.loc[:,"密度"]=df.loc[:,"密度"].astype(float)


for i in range(len(df)):
    if df.loc[i,"坡度"]<10:
        df.loc[i, "保留株数"]=56
    elif df.loc[i,"坡度"]<30:
        df.loc[i, "保留株数"] =65
    else:
        df.loc[i, "保留株数"] = 72

for i in range(len(df)):
    if df.loc[i, "密度"]>100:
        max_kan=int(df.loc[i, "密度"]*0.3)#0.3
    elif df.loc[i, "密度"]>85:
        max_kan = int(df.loc[i, "密度"] * 0.25)#0.25
    else:
        max_kan = int(df.loc[i, "密度"] * 0.2)#0.2
    if (df.loc[i,"密度"]-df.loc[i, "保留株数"])>max_kan:
        df.loc[i, "保留株数"]=df.loc[i,"密度"]-max_kan

for i in range(len(df)):
    if df.loc[i, "密度"]<df.loc[i, "保留株数"]:
        df.loc[i, '补植株数'] = df.loc[i, "保留株数"]-df.loc[i, "密度"]
        df.loc[i, "苗木量"] = int(df.loc[i, '补植株数'] * df.loc[i, '作业面积'])
    else:
        df.loc[i, '补植株数']=0


df.loc[:,"有机肥量"]=df.loc[:,"苗木量"]*2.5
df.loc[:,"苗木费"]=df.loc[:,"苗木量"]*8
df.loc[:,"有机肥"]=df.loc[:,"有机肥量"]*1.2

df.loc[df.loc[:,"营林方式"]=='低改',"复合肥量"]=df.loc[:,"保留株数"]*df.loc[:,"作业面积"]*1.5
df.loc[df.loc[:,"营林方式"]=='低改+水肥',"水溶肥量"]=df.loc[:,"保留株数"]*df.loc[:,"作业面积"]*1.5
df.loc[:,"复合肥量"]=round_preserve_sum_series(df.loc[:,"复合肥量"], decimals=0)
df.loc[:,"水溶肥量"]=round_preserve_sum_series(df.loc[:,"水溶肥量"], decimals=0)

df.loc[df.loc[:,"营林方式"]=='低改',"复合肥"]=df.loc[:,"复合肥量"]*4
df.loc[df.loc[:,"营林方式"]=='低改+水肥',"水溶肥"]=df.loc[:,"水溶肥量"]*7



#zhu=(19291*3453-np.nansum(df[["林分清理","整枝修剪","垦复","施肥","割灌除草","全面铲草","病虫害防控",'药剂费','扩宽条带、修筑高水平梯带等其他费用','复合肥','水溶肥','苗木费','有机肥']]))/11  #0827删除"密度调整"
mudu_f=(19291*3453-np.nansum(df[["林分清理","整枝修剪","垦复","施肥","割灌除草","全面铲草","病虫害防控",'药剂费','扩宽条带、修筑高水平梯带等其他费用','复合肥','水溶肥','苗木费','有机肥']]))/180/19291
df.loc[:,"密度调整"]=df.loc[:,"作业面积"]*mudu_f*180

#df_pei=df[['小班号','作业面积', '营林方式',"密度","保留株数"]]
#df_pei.to_excel(r"F:\HDY\202506河池油茶低改和单水肥\环江表格\环江株数配平0704.xlsx")
#28350

#buzhi=pd.read_excel(r"F:\HDY\202506河池油茶低改和单水肥\环江表格\环江株数配平0704.xlsx")#0827删除
#df.loc[:,'补植株数']=buzhi.loc[:,'补植']#0827删除
#df.loc[:,"间伐株数"]=df.loc[:,"密度"]+df.loc[:,"补植株数"]-df.loc[:,"保留株数"]#0827删除
#df.loc[:,"苗木量"]=df.loc[:,"补植株数"]*df.loc[:,"作业面积"]#0827删除
#df.loc[:,"有机肥量"]=df.loc[:,"补植株数"]*df.loc[:,"作业面积"]*2.5#0827删除
#df.loc[:,"苗木量"]=round_preserve_sum_series(df.loc[:,"苗木量"], decimals=0)#0827删除
#df.loc[:,"有机肥量"]=round_preserve_sum_series(df.loc[:,"有机肥量"], decimals=0)#0827删除


for filed in ["林分清理","密度调整","整枝修剪","垦复","施肥","割灌除草","全面铲草","病虫害防控",'药剂费','扩宽条带、修筑高水平梯带等其他费用','复合肥','水溶肥',"苗木费","有机肥",'密度调整']:
    df.loc[:,filed]=round_preserve_sum_series(df.loc[:,filed], decimals=0)
    print(filed+" "+str(df.loc[:,filed].sum()))
"""
amount=19291*3453-np.nansum(df[["林分清理","密度调整","整枝修剪","垦复","施肥","割灌除草","全面铲草","病虫害防控",'药剂费',
                                '扩宽条带、修筑高水平梯带等其他费用','复合肥','水溶肥',"苗木费","有机肥"]])
if abs(amount)<=50:
    df2=df.loc[df.loc[:,"补植株数"]>0,]
    max_area_idx = df2['作业面积'].idxmax()
    # Subtract 29 from the '费用' in that row
    df.loc[max_area_idx, '有机肥']=df.loc[max_area_idx, '有机肥']+amount
else:
    print(amount)

for filed in ["林分清理","密度调整","整枝修剪","垦复","施肥","割灌除草","全面铲草","病虫害防控",'药剂费','扩宽条带、修筑高水平梯带等其他费用','复合肥','水溶肥',"苗木费","有机肥"]:
    df.loc[:,filed]=round_preserve_sum_series(df.loc[:,filed], decimals=0)
    print(filed+" "+str(df.loc[:,filed].sum()))
"""
for i in range(len(df)):
    age=int(df.loc[i,"树龄"])
    guo=int(df.loc[i,"亩产鲜果"])
    if age<8:
        age=8
    if guo>250:
        zhen=(guo - 150) // 100
        yu=(guo - 150)%(100*zhen)
        re=yu*100/(100*zhen)+150
    else:
        re=guo
    df.loc[i, "树龄"]=str(age)
    df.loc[i, "亩产鲜果"] = str(int(re))

df = df.sort_values(by='小班号').reset_index(drop=True)
df.loc[:,"序号"]=df.index+1
df.loc[pd.isna(df.loc[:,"补植株数"]),"补植株数"]=0
df.loc[:,"间伐株数"]=df.loc[:,"密度"]+df.loc[:,"补植株数"]-df.loc[:,"保留株数"]

df.loc[:,"产期"]='盛产期'
tb1=df[['序号','县区','乡镇林场','村分场','小班号', '林地权属','作业面积','地形地势','海拔','坡向','坡度','坡位',
        '土壤类型','土层厚度','A层厚度','土壤质地','品种1', '树龄', '产期','平均树高','平均地径','平均冠幅',
        '盖度', '密度','亩产鲜果', '灾害类型']]

fileds1=['序号','县（区）','乡镇（林场）','村（分场）','小班号','林地权属','作业面积','地形地势','海拔','坡向','坡度','坡位',
        '土壤类型','土层厚度','腐殖质层厚度','土壤质地','主栽品种','树龄','产期','平均树高','平均地径','平均冠幅',
          '盖度','种植密度','亩产鲜果','灾害类型']
tb1.columns=fileds1
tb1.to_excel(r'F:\HDY\202604河池油茶更新\环江毛南族自治县\环江低改v202605\表格\TB1.xlsx')


tb2=df[['序号','县区','乡镇林场','村分场','经营主体', '联系方式','小班号','作业面积', '营林方式','密度','间伐株数','补植株数','保留株数',"垦复松土",'苗木量','有机肥量','复合肥量','水溶肥量','实施年度']]
fileds2=['序号','县（区）','乡镇（林场）','村（分场）','经营主体','联系方式','小班号','作业面积（亩）','营林模式','原始株数','间伐株数','补植株数','保留株数',"垦复方式",'需苗量','有机肥','复合肥','水溶肥','实施年度']
tb2.columns=fileds2
tb2.to_excel(r'F:\HDY\202604河池油茶更新\环江毛南族自治县\环江低改v202605\表格\TB2.xlsx')

df.loc[:,'肥料费']=np.nansum(df[['有机肥','复合肥','水溶肥']],axis=1)
df.loc[:,"小计"]=np.nansum(df[["林分清理","密度调整","整枝修剪","垦复","施肥","割灌除草","全面铲草","病虫害防控"]],axis=1)
df.loc[:,"合计"]=np.nansum(df[["小计",'苗木费','肥料费',"药剂费",'扩宽条带、修筑高水平梯带等其他费用']],axis=1)

tb3=df[['序号','县区','乡镇林场','村分场','经营主体','小班号','作业面积','营林方式','合计',
        '苗木费','肥料费',"药剂费",'小计','林分清理','密度调整','整枝修剪','垦复','施肥','割灌除草','全面铲草','病虫害防控',
         '扩宽条带、修筑高水平梯带等其他费用']]

fileds3=['序号','县（区）','乡镇（林场）','村（分场）','经营主体','小班号','作业面积','营林模式','合计',
         '苗木费','肥料费',"药剂费",'小计','林分清理','密度调整','整枝修剪','垦复','追肥','割灌除草','全面铲草','病虫害防控',
         '扩宽条带、修筑高水平梯带等其他费用']
tb3.columns=fileds3
tb3.to_excel(r'F:\HDY\202604河池油茶更新\环江毛南族自治县\环江低改v202605\表格\TB3.xlsx')

tj=df[['乡镇林场','村分场', '作业面积']]
tj.loc[:,'数量']=1
tj=tj.groupby(['乡镇林场','村分场']).sum()
#tj_reshaped = tj.unstack(level='乡镇林场')
#tj_reshaped = tj_reshaped.reset_index()
tj.to_csv(r"F:\HDY\202604河池油茶更新\环江毛南族自治县\环江低改v202605\表格\TJ.csv")



##################################    附加案例2  靖安县国土绿化（标准化）  ###################################################
import geopandas as gpd
import pandas as pd
import numpy as np
def generate_plot_numbers(gdf,F1,fields):
    gdf['centroid'] = gdf.geometry.centroid
    gdf['centroid_x'] = gdf['centroid'].x
    gdf['centroid_y'] = gdf['centroid'].y

    # 按照乡镇、村、经营主体分组，然后在每组内按从左到右(先x后y)排序
    gdf = gdf.sort_values(by=fields+['centroid_x', 'centroid_y'])

    # 生成小班号
    gdf.loc[:,F1] = range(1, len(gdf) + 1)
    # 删除临时列
    gdf = gdf.drop(columns=['centroid', 'centroid_x', 'centroid_y'])
    return gdf
def round_preserve_sum_series(series, decimals=0):
    """
    对Pandas Series进行四舍五入并保持总和不变
    """
    # 初步四舍五入
    rounded = series.round(decimals)

    # 计算差异
    difference = round(series.sum(), decimals) - round(rounded.sum(), decimals)

    # 如果存在差异，调整数值
    if difference != 0:
        # 计算余数
        remainders = series - rounded

        # 找出余数最大的几个值进行调整
        adjustment = int(round(difference * (10 ** decimals)))
        to_adjust = remainders.abs().nlargest(abs(adjustment)).index

        # 应用调整
        for i in to_adjust:
            rounded[i] += np.sign(difference) * (10 ** -decimals)
    return rounded
def cal_miaomu(data):
    danjia=pd.read_excel(r"F:\HDY\202508赣西国土绿化\作业设计第二版\苗木单价表.xlsx",index_col=0)
    for i in range(3):
        for j in range(len(data)):
            if data.loc[j,"树种"+str(i+1)+"亩株数"]>0:
                data.loc[j, "树种" + str(i + 1) + "总株数"] = round(int(data.loc[j,"树种"+str(i+1)+"亩株数"])*data.loc[j,"小班面积"],0)
                shuzhong=data.loc[j, "树种" + str(i + 1)]
                data.loc[j, "树种" + str(i + 1) + "总价格"] = data.loc[j, "树种" + str(i + 1) + "总株数"]*danjia.loc[shuzhong,'单价（元）']
            else:
                data.loc[j, "树种" + str(i + 1) + "总株数"]=0
                data.loc[j, "树种" + str(i + 1) + "总价格"] =0
    data.loc[:,"苗木总株数"]=np.nansum(data.loc[:,["树种1总株数","树种2总株数","树种3总株数"]],axis=1)
    data.loc[:, "苗木费"] = np.nansum(data.loc[:, ["树种1总价格", "树种2总价格", "树种3总价格"]], axis=1)
    return data

price=pd.read_excel(r'F:\HDY\202508赣西国土绿化\作业设计第二版\单价表.xlsx')
for i in range(len(price)):
    result=str(price.loc[i,"序号"]).split('.')
    for j in range(len(result)):
        price.loc[i, "tp"+str(j+1)] = result[j]

#转为字典
dict1 = {}
types = pd.unique(price.loc[:,"tp1"])
for type in types:
    price_type = price.loc[price.loc[:, "tp1"] == type,].reset_index(drop=True)
    name=price_type.loc[0,"项目建设内容"]
    dict2={"合计":price_type.loc[0,"合计"]}
    price_type=price_type.loc[1:,:].reset_index(drop=True)
    types2=pd.unique(price_type.loc[:,"tp2"])
    for type2 in types2:
        price_type2 = price_type.loc[price_type.loc[:, "tp2"] == type2,].reset_index(drop=True)
        name2=price_type2.loc[0,'项目建设内容']
        price_type2 = price_type2.loc[1:,:].reset_index(drop=True)
        types3 = pd.unique(price_type2.loc[:, "tp3"])
        dict3={}
        for type3 in types3:
            price_type3 = price_type2.loc[price_type2.loc[:, "tp3"] == type3,].reset_index(drop=True)
            name3 = price_type3.loc[0, '项目建设内容']
            dict4={"项目建设内容":price_type3.loc[0,"项目建设内容"],"单位":price_type3.loc[0,"单位"],
                   "数量":price_type3.loc[0,"数量"],'综合单价':price_type3.loc[0,"综合单价"]}
            dict3.update({name3:dict4})
        dict2.update({name2:dict3})
    dict1.update({name:dict2})

df=gpd.read_file(r"F:\HDY\202508赣西国土绿化\作业设计第二版\赣西第二版.gdb",layer='靖安1021')#
df=df.loc[df.loc[:,"备注"]!='替补地块',:].reset_index(drop=True)
df.loc[:,'小班面积']=round(df.loc[:,'小班面积'],1)
df.loc[:,'亩蓄积']=round(df.loc[:,'亩蓄积'],3)
df.loc[:,'亩采伐蓄积']=round(df.loc[:,'亩采伐蓄积'],3)
df.loc[:,'作业后郁闭度']=round(df.loc[:,'作业后郁闭度'],2)
df.loc[:,'郁闭度']=round(df.loc[:,'郁闭度'],2)
df.loc[:,'平均胸径']=round(df.loc[:,'平均胸径'],1)

df=generate_plot_numbers(df,F1='作业号',fields=['sort','县', '乡镇_场_', '村_分场_'])

###更新绿化类型
beixuan=['Ⅰ','Ⅱ','Ⅲ','Ⅳ','Ⅴ','Ⅵ','Ⅶ','Ⅷ','Ⅸ','Ⅹ','Ⅺ','Ⅻ','XIII','XIV','XV','XVI','XVII','XVIII','XIX','XX']
LS=pd.unique(df.loc[:,'立地类型'])
ldi={}
for i in range(len(LS)):
    ldi.update({LS[i]:beixuan[i]})

tb_ldi=pd.DataFrame()
for L in LS:
    data=df.loc[df.loc[:,'立地类型']==L,:]
    tb_ldi.loc[L,"立地类型号"]=ldi[L]
    tb_ldi.loc[L,"土壤类型"]=str(pd.unique(data.loc[:,"土壤类型"])).replace("'","").replace("[","").replace("]","")
    tb_ldi.loc[L, "土壤质地"]=str(pd.unique(data.loc[:,"土壤质地"])).replace("'","").replace("[","").replace("]","")
    tb_ldi.loc[L,"主要乔木"]=str(pd.unique(data.loc[:,"优势树种"])).replace("'","").replace("[","").replace("]","")
    tb_ldi.loc[L, "主要灌草"]=str(pd.unique(data.loc[:,"林下植被主要类型"])).replace("'","").replace("[","").replace("]","")
tb_ldi.to_excel(r"F:\HDY\202508赣西国土绿化\作业设计第一版\表格\立地类型表格.xlsx")

for i in range(len(df)):
    df.loc[i,'立地类型']=ldi[df.loc[i,'立地类型']]
tb_ldi=pd.DataFrame({'中文':ldi.keys(),'罗马':ldi.values()})


###添加绿化模式
green_modes=pd.read_excel(r'F:\HDY\202508赣西国土绿化\作业设计第二版\表格\绿化模式.xlsx')
for i in range(len(df)):
    if df.loc[i,'建设方式']!='中幼林抚育':
        df_mode=green_modes.loc[green_modes.loc[:,'绿化模式']==df.loc[i,'建设方式'],:].reset_index(drop=True)
        df_mode = df_mode.loc[df_mode.loc[:, '树种'] ==df.loc[i,'补植比例'], :].reset_index(drop=True)
        df.loc[i, '绿化模式']=df_mode.loc[0,'命名']
        df.loc[i, '绿化模型'] = df_mode.loc[0, '绿化模型']

LS=pd.unique(df.loc[:,'绿化模型'])
tb_type=pd.DataFrame()
for L in LS:
    data=df.loc[df.loc[:,'绿化模型']==L,:]
    tb_type.loc[L, "绿化模式"] = str(pd.unique(data.loc[:, "绿化模式"])).replace("'", "").replace("[", "").replace("]","")
    tb_type.loc[L,"立地类型"]=str(pd.unique(data.loc[:,"立地类型"])).replace("'","").replace("[","").replace("]","")
    tb_type.loc[L, "林种"]=str(pd.unique(data.loc[:,"林种"])).replace("'","").replace("[","").replace("]","")
    tb_type.loc[L, "补植比例"] = str(pd.unique(data.loc[:, "补植比例"])).replace("'", "").replace("[", "").replace("]", "")
    min=np.nanmin(data.loc[:, "造林密度调整后"])
    max=np.nanmax(data.loc[:, "造林密度调整后"])
    if np.isnan(min)==False:
        tb_type.loc[L, "造林密度"]=str(min)+"~"+str(max)

tb_type.to_excel(r"F:\HDY\202508赣西国土绿化\作业设计第一版\表格\附表2xx.xlsx")

huizong=pd.DataFrame()
types=pd.unique(df.loc[:,"建设方式"])
for type in types:
    dfs_yr=df.loc[df.loc[:,"建设方式"]==type,:].reset_index(drop=True)
    value=dict1[type]['合计']*dfs_yr.loc[:,"小班面积"].sum()
    my_dict=dict1[type].copy()
    my_dict.pop('合计')
    for key in my_dict.keys():
        my_dict2=my_dict[key]
        for key2 in my_dict2.keys():
            if my_dict2[key2]['单位']=='工日':
                dfs_yr.loc[:, key2+"用工量"] =dfs_yr.loc[:, '小班面积']*my_dict2[key2]['数量']
                dfs_yr.loc[:, key2] =dfs_yr.loc[:, '小班面积']*my_dict2[key2]['数量']*my_dict2[key2]['综合单价']
            elif my_dict2[key2]['单位'] == '株':
                dfs_yr=cal_miaomu(dfs_yr)
            elif my_dict2[key2]['单位'] == '千克/株':
                dfs_yr.loc[:, key2+'量'] = dfs_yr.loc[:, "苗木总株数"] * my_dict2[key2]['数量']
                dfs_yr.loc[:,key2]=dfs_yr.loc[:, key2 + '量']*my_dict2[key2]['综合单价']

            elif my_dict2[key2]['单位'] == '千克/亩':
                dfs_yr.loc[:, key2+'量'] = dfs_yr.loc[:, '小班面积'] * my_dict2[key2]['数量']
                dfs_yr.loc[:, key2] = dfs_yr.loc[:, key2 + '量'] * my_dict2[key2]['综合单价']
            dfs_yr.loc[:, key2] = round_preserve_sum_series(dfs_yr.loc[:, key2])
        dfs_yr.loc[:, key] = np.nansum(dfs_yr[my_dict2.keys()],axis=1)

    #调整采伐工日
    dfs_yr.loc[dfs_yr.loc[:,"备注"].isin(["示范点",'示范点、监测点']),"示范点费用"]=10000
    fd=my_dict[list(my_dict.keys())[0]][list(my_dict[list(my_dict.keys())[0]].keys())[0]]['项目建设内容']
    value_real=np.nansum(dfs_yr[my_dict.keys()])+np.nansum(dfs_yr.loc[:,"示范点费用"])
    ra=(value-value_real)/np.nansum(dfs_yr.loc[:, '小班面积'])/180
    print(type+" "+str(ra))
    dfs_yr.loc[:, fd]=dfs_yr.loc[:, fd]+ra*180*dfs_yr.loc[:, '小班面积']
    dfs_yr.loc[:, fd]=round_preserve_sum_series(dfs_yr.loc[:, fd],0)

    for key in my_dict.keys():
        my_dict2=my_dict[key]
        dfs_yr.loc[:, key] = np.nansum(dfs_yr[my_dict2.keys()],axis=1)
    dfs_yr.loc[:, fd+'用工量'] = dfs_yr.loc[:, fd]/180
    dfs_yr.loc[:, fd + '用工量']=round_preserve_sum_series(dfs_yr.loc[:, fd + '用工量'],2)
    dfs_yr.to_csv("F:/HDY/202508赣西国土绿化/作业设计第一版/df" + str(type) + ".csv")
    huizong=pd.concat([huizong,dfs_yr]).reset_index(drop=True)

#huizong.to_excel(r"F:\HDY\202508赣西国土绿化\作业设计第一版\表格\资金.xlsx")






lst=[]
for f in huizong.columns:
    if '用工量' in f:
        lst.append(f)
huizong.loc[:,'用工量']=np.nansum(huizong[lst],axis=1)
huizong[['建设方式','用工量']].groupby('建设方式').sum()


huizong[['作业号','用工量']].to_excel(r"F:\HDY\202508赣西国土绿化\作业设计第二版\表格\用工量更新.xlsx")
###表格制作
shuzhong=['木荷', '南酸枣', '闽楠', '杉木', '湿地松', '檫木', '枫香',  '杂交马褂木']
for i in range(len(shuzhong)):
    lst=[]
    for j in range(len(huizong)):
        if shuzhong[i]==str(huizong.loc[j,'树种1']) or shuzhong[i]==str(huizong.loc[j,'树种2']) or shuzhong[i]==str(huizong.loc[j,'树种3']):
            lst.append(huizong.loc[j,'绿化模式'])
    print(shuzhong[i]+str(pd.unique(lst)))



#附表1
table1_1=huizong[huizong.loc[:,'建设方式']=="中幼林抚育"].reset_index(drop=True)
table1_1=table1_1[['县', '乡镇_场_', '村_分场_','作业号', '小班面积','实施年度','土地所有权', '林木所有权', '林木使用权','现状地类','国土三调地类','林种', '森林类别','公益林事权等级',
        '地貌', '海拔', '坡向', '坡位', '坡度','土壤类型','土壤质地', '土层厚度', '腐殖质厚度','林下植被主要类型','林下植被盖度','起源','树种组成',
        '年龄', '龄组', '郁闭度','平均胸径', '平均树高','亩株数', '亩蓄积','天然更新等级']]
table1_1.to_excel(r'F:\HDY\202508赣西国土绿化\作业设计第二版\表格\table1_1.xlsx')

table1_2=huizong[huizong.loc[:,'建设方式']=="补植修复"].reset_index(drop=True)
table1_2=table1_2[['县', '乡镇_场_', '村_分场_','作业号', '小班面积','实施年度','土地所有权', '林木所有权', '林木使用权','现状地类','国土三调地类','林种', '森林类别','公益林事权等级',
        '地貌', '海拔', '坡向', '坡位', '坡度','土壤类型','土壤质地', '土层厚度', '腐殖质厚度','林下植被主要类型','林下植被盖度','起源','树种组成',
        '年龄', '龄组', '郁闭度','平均胸径', '平均树高','亩株数', '亩蓄积','灾害类型','枯死木和濒死木株数比例','天然更新等级']]
table1_2.to_excel(r'F:\HDY\202508赣西国土绿化\作业设计第二版\表格\table1_2.xlsx')

table1_3=huizong[huizong.loc[:,'建设方式']=="补植改培"].reset_index(drop=True)
table1_3=table1_3[['县', '乡镇_场_', '村_分场_','作业号', '小班面积','实施年度','土地所有权', '林木所有权', '林木使用权','现状地类','国土三调地类','林种', '森林类别','公益林事权等级',
        '地貌', '海拔', '坡向', '坡位', '坡度','土壤类型','土壤质地', '土层厚度', '腐殖质厚度','林下植被主要类型','林下植被盖度','起源','树种组成',
        '年龄', '龄组', '郁闭度','平均胸径', '平均树高','亩株数', '亩蓄积','灾害类型','枯死木和濒死木株数比例','天然更新等级']]
table1_3.to_excel(r'F:\HDY\202508赣西国土绿化\作业设计第二版\表格\table1_3.xlsx')

table1_4=huizong[huizong.loc[:,'建设方式']=="人工造林"].reset_index(drop=True)
table1_4=table1_4[['县', '乡镇_场_', '村_分场_','作业号', '小班面积','实施年度','土地所有权', '林木所有权', '林木使用权','现状地类','国土三调地类','林种', '森林类别','公益林事权等级',
        '地貌', '海拔', '坡向', '坡位', '坡度','土壤类型','土壤质地', '土层厚度', '腐殖质厚度','林下植被主要类型','林下植被盖度','天然更新等级']]
table1_4.to_excel(r'F:\HDY\202508赣西国土绿化\作业设计第二版\表格\table1_4.xlsx')

#附表5
table5_1=huizong[huizong.loc[:,'建设方式']=="中幼林抚育"].reset_index(drop=True)
table5_1.loc[table5_1.loc[:,'龄组']=='幼龄林','采伐方式']="透光伐"
table5_1.loc[table5_1.loc[:,'龄组']=='中龄林','采伐方式']="疏伐"
table5_1.loc[:,'作业前亩株数']=table5_1.loc[:,'亩株数'].round(0)
table5_1.loc[:,'作业前亩蓄积']=table5_1.loc[:,'亩蓄积'].round(3)
table5_1.loc[:,'作业前郁闭度']=table5_1.loc[:,'郁闭度'].round(2)
table5_1.loc[:,'作业前平均胸径']=table5_1.loc[:,'平均胸径'].round(1)
table5_1.loc[:,"株数采伐量"]=(table5_1.loc[:,'亩采伐株数_株_']*table5_1.loc[:,'小班面积']).round(0)
table5_1.loc[:,"蓄积采伐量"]=(table5_1.loc[:,'亩采伐蓄积']*table5_1.loc[:,'小班面积']).round(3)
table5_1.loc[:,'作业后亩株数']=(table5_1.loc[:,'亩株数']-table5_1.loc[:,'亩采伐株数_株_']).round(0)
table5_1.loc[:,'作业后亩蓄积']=((table5_1.loc[:,'亩蓄积']-table5_1.loc[:,'亩采伐蓄积'])).round(3)
table5_1.loc[:,'作业后平均胸径']=table5_1.loc[:,'作业后胸径'].round(2)

table5_1=table5_1[['县', '乡镇_场_', '村_分场_','作业号', '小班面积','实施年度', '绿化模型','绿化模式','立地类型',"林种",'采伐方式','主要采伐树种',"作业前郁闭度","作业后郁闭度",
        "作业前平均胸径","作业后平均胸径",'平均树高','作业前亩株数','作业后亩株数','作业前亩蓄积','作业后亩蓄积','株数采伐强度', '蓄积采伐强度',"株数采伐量","蓄积采伐量",
        "用工量","备注"]]
table5_1.to_excel(r'F:\HDY\202508赣西国土绿化\作业设计第二版\表格\table5_1.xlsx')

table5_2=huizong[huizong.loc[:,'建设方式']=="补植修复"].reset_index(drop=True)
table5_2.loc[:,"整地方式"]='穴状整地'
table5_2.loc[:,"整地规格"]='50*50*40'
spps=[]
for i in range(len(table5_2)):
    for j in range(3):
        spp=table5_2.loc[i,"树种"+str(j+1)]
        if spp!='':
            value_spp=table5_2.loc[i,"树种"+str(j+1)+"总株数"]
            table5_2.loc[i,spp]=value_spp
            if spp not in spps:
                spps.append(spp)

table5_2=table5_2[['县', '乡镇_场_', '村_分场_','作业号', '小班面积','实施年度', '绿化模型','绿化模式','立地类型','林种','主要采伐树种','亩采伐株数_株_',
       '亩采伐蓄积', '株数采伐强度', '蓄积采伐强度','补植比例',"造林密度调整后","整地方式","整地规格"]+spps+["基肥量","追肥量","用工量","备注"]]
table5_2.to_excel(r'F:\HDY\202508赣西国土绿化\作业设计第二版\表格\table5_2.xlsx')

table5_3=huizong[huizong.loc[:,'建设方式']=="补植改培"].reset_index(drop=True)
table5_3.loc[:,"整地方式"]='穴状整地'
table5_3.loc[:,"整地规格"]='50*50*40'
spps=[]
for i in range(len(table5_3)):
    for j in range(3):
        spp=table5_3.loc[i,"树种"+str(j+1)]
        if spp!='':
            value_spp=table5_3.loc[i,"树种"+str(j+1)+"总株数"]
            table5_3.loc[i,spp]=value_spp
            if spp not in spps:
                spps.append(spp)
table5_3=table5_3[['县', '乡镇_场_', '村_分场_','作业号', '小班面积','实施年度', '绿化模型','绿化模式','立地类型','林种','主要采伐树种','亩采伐株数_株_',
       '亩采伐蓄积', '株数采伐强度', '蓄积采伐强度','补植比例',"造林密度调整后","整地方式","整地规格"]+spps+["基肥量","追肥量","用工量","备注"]]
table5_3.to_excel(r'F:\HDY\202508赣西国土绿化\作业设计第二版\表格\table5_3.xlsx')

table5_4=huizong[huizong.loc[:,'建设方式']=="人工造林"].reset_index(drop=True)
table5_4.loc[table5_4.loc[:,"造林密度调整后"]=='133',"株行距"]='2*2.5'
table5_4.loc[table5_4.loc[:,"造林密度调整后"]=='111',"株行距"]='2*3'
spps=[]
for i in range(len(table5_4)):
    for j in range(3):
        spp=table5_4.loc[i,"树种"+str(j+1)]
        if spp!='':
            value_spp=table5_4.loc[i,"树种"+str(j+1)+"总株数"]
            table5_4.loc[i,spp]=value_spp
            if spp not in spps:
                spps.append(spp)
table5_4.loc[:,"整地方式"]='穴状整地'
table5_4.loc[:,"整地规格"]='50*50*40'
table5_4=table5_4[['县', '乡镇_场_', '村_分场_','作业号', '小班面积','实施年度', '绿化模型','绿化模式','立地类型',"林种",'补植比例','株行距',"造林密度调整后",
                    "整地方式","整地规格"]+spps+["基肥量","追肥量",'农药量',"用工量","备注"]]

table5_4.to_excel(r'F:\HDY\202508赣西国土绿化\作业设计第二版\表格\table5_4.xlsx')

table7=huizong.copy()
table7.loc[:,'抚育、除草、施肥、打药']=np.nansum(table7[['抚育、除草、施肥','抚育、除草、施肥、打药']],axis=1)
table7.loc[:,'林地清理/采伐剩余物清理']=np.nansum(table7[['林地清理','林地清理/采伐剩余物清理']],axis=1)
table7=table7[['县', '乡镇_场_', '村_分场_','作业号', '小班面积', '建设方式',"苗木费",'基肥','追肥','农药','采伐','林地清理/采伐剩余物清理','整地、挖穴',
               '施基肥、回表土','栽植','抚育、除草、施肥、打药','次年抚育','第三年抚育','未成造补植','示范点费用']]
table7.to_excel(r"F:\HDY\202508赣西国土绿化\作业设计第二版\表格\Table7.xlsx")

for f in ["苗木费",'基肥','追肥','农药','采伐','林地清理/采伐剩余物清理','整地、挖穴','施基肥、回表土','栽植','抚育、除草、施肥、打药','次年抚育','第三年抚育','未成造补植','示范点费用']:
    print(f+" "+str(table7.loc[:,f].sum()))


table7.to_excel(r'F:\HDY\202508赣西国土绿化\作业设计第二版\表格\table7.xlsx')
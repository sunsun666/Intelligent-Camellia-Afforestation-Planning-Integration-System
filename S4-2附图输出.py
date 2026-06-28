import matplotlib
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimSun']  # Windows
plt.rcParams['axes.unicode_minus'] = False
from osgeo import gdal
def geotif_read(path):
    dataset = gdal.Open(path)
    # 获取图像大小
    rows = dataset.RasterYSize
    cols = dataset.RasterXSize
    bands = dataset.RasterCount
    # 获取地理参考信息
    geotransform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()

    # 读取像素值
    band = dataset.GetRasterBand(1)  # 选择第一个波段
    data = band.ReadAsArray(0, 0, cols, rows)  # 读取整个图像
    # 关闭文件
    dataset = {"rows":rows,"cols":cols,"bands":bands,"geotransform":geotransform,"projection":projection,"data":data}
    return dataset
def trans_to_table(dataframe):
    df_re=[]
    for i in range(len(dataframe)):
        df_re.append(list(dataframe.loc[i,:]))
    return df_re

def get_circle(x1, y1, x2, y2, x3, y3):
    """
    根据三个点，返回外接圆的中心和半径
    :param x1:
    :param y1:
    :param x2:
    :param y2:
    :param x3:
    :param y3:
    :return: x,y,r
    """
    a = x1 - x2
    b = y1 - y2
    c = x1 - x3
    d = y1 - y3
    a1 = ((x1 * x1 - x2 * x2) + (y1 * y1 - y2 * y2)) / 2.0
    a2 = ((x1 * x1 - x3 * x3) + (y1 * y1 - y3 * y3)) / 2.0
    theta = b * c - a * d
    #if abs(theta) < 1e-7:
    #    raise ValueError("compute circle error!")
    x0 = (b * a2 - d * a1) / theta
    y0 = (c * a1 - a * a2) / theta
    r = np.sqrt(pow((x1 - x0), 2) + pow((y1 - y0), 2))
    return x0, y0, r

def add_north(ax, x, y, text_size=15, arrow_width=0.05,
              text_pad=0.01, arrow_height=None,
              line_width=1, add_circle=True):
    """
    给子图添加一个指北针，这里的长度，间隔等是0-1之间的小数
    :param ax: 子图句柄
    :param x: 指针尖的x坐标[0-1]
    :param y: 指针尖的y坐标[0-1]
    :param text_size: N字符大小
    :param arrow_width: 箭头的宽度
    :param text_pad: 文字和箭头的间隔
    :param arrow_height: 箭头的宽度
    :param line_width: 线条的宽度
    :param add_circle: 是否添加圆
    :return: None
    """
    if arrow_height is None:
        arrow_height = arrow_width * 1.87
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    width = x_max - x_min
    height = y_max - y_min

    left = (x_min + width * (x - arrow_width * 0.5), y_min + height * (y - arrow_height))
    right = (x_min + width * (x + arrow_width * 0.5), left[1])
    top = (x_min + width * x, y_min + height * y)
    bottom_center = (top[0], left[1] + 0.27 * (top[1] - left[1]))
    left_patch = Polygon([left, top, bottom_center], color='k',
                         linewidth=line_width)
    right_patch = Polygon([bottom_center, top, right],
                          facecolor='none',
                          edgecolor='k', linewidth=line_width)
    ax.add_patch(left_patch)
    ax.add_patch(right_patch)
    if add_circle:
        circle_x, circle_y, r = get_circle(top[0],top[1], left[0],left[1], right[0],right[1])

        circle_patch = Circle((circle_x, circle_y), r,
                              facecolor='none',
                              edgecolor='k',
                              linewidth=line_width)
        ax.add_patch(circle_patch)

    ax.text(s='N',
            x=top[0],
            y=top[1] + text_pad * height,
            fontsize=text_size,
            horizontalalignment='center',
            verticalalignment='bottom')


###########################################矢量
from shapely.geometry import Point
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.geometry import box
from shapely import set_precision
from math import atan2, degrees
#import matplotlib
#atplotlib.use('Agg')  # 必须在导入 pyplot 之前设置
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.image as mpimg
import matplotlib.font_manager as fm
from matplotlib.patches import *
import cartopy.crs as ccrs
from cartopy.crs import Mercator
plt.rcParams['font.family'] = 'SimHei'  # 宋体的英文名称
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
from cartopy.io.img_tiles import TDT_img
tiler = TDT_img()

def scale_bar(ax, x=0.1, y=0.9, w=60, h=0.01):
    #画比例尺函数
    # x代表比例尺开始的经度
    # y代表比例尺所在纬度
    # length代表比例尺的长度，单位为多少个经度
    # low代表竖刻度线的y最小值调节距离
    # up代表竖刻度线的y最大值调节距离
    # xtext代表文字的x调节距离
    # ytext代表文字的y调节距离
    # lw代表比例尺的宽度
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    width = x_max - x_min
    height = y_max - y_min

    x = x_min+x*width
    y = y_min+y*height
    h = h*height
    wlsit=[x,x + w,x + 2 * w,x + 4 * w,x+6*w]
    textlist=[0,w,2*w,4*w,6*w]
    rect1 = plt.Rectangle((x, y), w, h, facecolor='black', edgecolor='black', linewidth=1)
    rect2 = plt.Rectangle((x + w, y), w, h, facecolor='white', edgecolor='black', linewidth=1)
    rect3 = plt.Rectangle((x + 2 * w, y), 2 * w, h, facecolor='black', edgecolor='black', linewidth=1)
    rect4 = plt.Rectangle((x + 4 * w, y), 2 * w, h, facecolor='white', edgecolor='black', linewidth=1)
    ax.add_patch(rect1)
    ax.add_patch(rect2)
    ax.add_patch(rect3)
    ax.add_patch(rect4)
    for i in range(5):
        ax.text(s=str(int(textlist[i])),
                x=wlsit[i],
                y=y-height*0.025,
                fontsize=12,
                horizontalalignment='center',
                verticalalignment='bottom')

def guide_line(ax, starx,starty,x_pin_scale=0.9,y_pin_scale=0.26526718):
    #画比例尺函数
    # x代表比例尺开始的经度
    # y代表比例尺所在纬度
    # length代表比例尺的长度，单位为多少个经度
    # low代表竖刻度线的y最小值调节距离
    # up代表竖刻度线的y最大值调节距离
    # xtext代表文字的x调节距离
    # ytext代表文字的y调节距离
    # lw代表比例尺的宽度
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    width = x_max - x_min
    height = y_max - y_min

    pinx=x_pin_scale*width+x_min
    piny=y_pin_scale*height+y_min

    ax.plot([starx,pinx],[starty,piny],color='red')
    ax.plot([pinx,x_max],[piny,piny],color='red')


crs=ccrs.PlateCarree


def calculaterotation(data, rg=10):
    gdf = data.copy().reset_index(drop=True)
    # 预创建三列，避免赋值失效
    gdf[["x", "y", "angle"]] = 0.0

    for s in range(len(gdf)):
        geom = gdf.loc[s, "geometry"]
        midpoint = geom.interpolate(0.5, normalized=True)

        # 中点裁剪方框
        bf = gpd.GeoDataFrame(
            geometry=[box(midpoint.x - rg, midpoint.y - rg, midpoint.x + rg, midpoint.y + rg)],
            crs=gdf.crs
        )
        # 截取局部线段
        line_clip = gpd.overlay(gdf.loc[[s]], bf, how="intersection")
        if len(line_clip) == 0:
            continue

        # 拆分多段线，取第一条单线
        line_explode = line_clip.explode(index_parts=True).reset_index(drop=True)
        single_line = line_explode.iloc[0]["geometry"]
        coords = list(single_line.coords)

        start = coords[0]
        end = coords[-1]
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        angle = degrees(atan2(dy, dx))

        # 文字正向校正
        if 90 <= angle < 270:
            angle -= 180

        gdf.loc[s, "x"] = midpoint.x
        gdf.loc[s, "y"] = midpoint.y
        gdf.loc[s, "angle"] = angle
    return gdf

def cal_bound(ra,leng_yan,x1,x2,y1,y2):
    ra2= (x2-x1+2*leng_yan)/(y2-y1+2*leng_yan)
    if ra2>ra:
        scaley=((x2-x1+2*leng_yan)/2)/ra
        minx=x1-leng_yan
        maxx=x2+leng_yan
        miny=(y2+y1)/2-scaley
        maxy=(y2+y1)/2+scaley
    else:
        scalex=((y2-y1+2*leng_yan)/2)*ra
        miny=y1-leng_yan
        maxy=y2+leng_yan
        minx=(x2+x1)/2-scalex
        maxx=(x2+x1)/2+scalex
    return minx,miny,maxx,maxy


counter=gpd.read_file(r'F:\HDY\202506河池油茶低改和单水肥\低改和单水肥数据库.gdb',layer='金城江等值线',engine='pyogrio')
counter = counter[counter["Contour"] % 10 == 0]
counter.loc[:,'Contour']=counter.loc[:,'Contour'].astype(int)


df1=gpd.read_file(r'F:\HDY\202506河池油茶低改和单水肥\金城江低改和单水肥文本1113\表格\金城江低改出图1113.gdb',layer='金城江低改出图1113',engine='pyogrio').to_crs(counter.crs)
df1.loc[:,'minx']=df1.bounds['minx']
df1.loc[:,'miny']=df1.bounds['miny']
df1.loc[:,'maxx']=df1.bounds['maxx']
df1.loc[:,'maxy']=df1.bounds['maxy']
df1.小班号=df1.小班号.astype(int)
df2=df1.to_crs(ccrs.PlateCarree())

image = mpimg.imread(r'C:\Users\Administrator\Pictures\background.png')  # 替换为你的图像路径
xiang = gpd.read_file(r'D:\000环江\00河池数据审核用.gdb',layer='河池乡镇界').to_crs(df1.crs)
xiang = xiang[xiang['XZQDM'].str.startswith('451202')]


import matplotlib.patheffects as path_effects
from matplotlib.backends.backend_pdf import PdfPages  # 新增1行
matplotlib.use('Agg')
pdf_out_path = r'F:/HDY/zyj/全部小班作业设计图汇总.pdf'
with PdfPages(pdf_out_path) as pdf:  # 外层包裹循环
    for i in range(len(df1)):
        fig = plt.figure(figsize=(16.5, 11.7))
        ax1 = plt.axes([0, 0, 1, 1])  # 左上角
        ax1.imshow(image)
        ax1.set_xticks([])  # 隐藏x轴刻度
        ax1.set_yticks([])  # 隐藏y轴刻度
        ax1.set_axis_off()
        ax1.text(
            x=387,
            y=400,
            s='河池市中财油茶发展示范奖补项目金城江区作业设计',
            fontsize=22,  # 字体大小
            color='black',
            ha='left',
        )
        ax1.text(
            x=4110,
            y=395,
            s='低产林改造小班作业设计图',
            fontsize=15,  # 字体大小
            color='black',
            ha='left',
        )
        ax1.plot([1200,1250],[1650+2,1650+2],color='red')
        # 4. 绘制裁剪后的等高线
        #leng_yan=50#/111625
        ra=0.362*16.5/( 11.7*0.6768)#1

        # ax2 位置图
        ax2 = plt.axes([0.014, 0.409, 0.228, 0.452])  # 左上角
        ax2.set_xticks([])  # 隐藏x轴刻度
        ax2.set_yticks([])  # 隐藏y轴刻度
        xiang_s=xiang.loc[0:5,:]
        xiang_s.plot(ax=ax2, facecolor='orange', edgecolor='gray')
        xiang.plot(ax=ax2, facecolor='none', edgecolor='gray')

        for idx, row in xiang.iterrows():
            # 获取多边形的几何中心点
            centroid = row.geometry.centroid
            # 在中心点位置添加文本标签
            ax2.text(centroid.x, centroid.y, row['XZQMC'],
                    fontsize=10, ha='center', va='center',
                    bbox=dict(facecolor='white', alpha=0, edgecolor='none', boxstyle='round,pad=0.2'))

        minx, miny, maxx, maxy=cal_bound(ra=0.228*16.5/(0.452*11.7),leng_yan=5000,x1=np.nanmin(xiang.bounds['minx']),
                                         x2=np.nanmax(xiang.bounds['maxx']),
                                         y1=np.nanmin(xiang.bounds['miny']),
                                         y2=np.nanmax(xiang.bounds['maxy']))
        bbox_plot=gpd.GeoDataFrame(
            geometry=[box(df1.loc[i,'minx'], df1.loc[i,'miny'], df1.loc[i,'maxx'], df1.loc[i,'maxy'])],
            crs=counter.crs).to_crs(xiang_s.crs)
        bbox_plot.plot(ax=ax2, facecolor='none', edgecolor='red',linewidth=2)
        plt.xlim(minx, maxx)
        plt.ylim(miny, maxy)

        # ax3地形图
        max_len=np.nanmax([df1.loc[i,'maxy']-df1.loc[i,'miny'],df1.loc[i,'maxx']-df1.loc[i,'minx']])
        scale=1+max_len*1.5/14//20#20是倍数控制
        max_len=scale*20*14
        """
        minx, miny, maxx, maxy=cal_bound(ra=ra,leng_yan=50,x1=df1.loc[i,'minx'],x2=df1.loc[i,'maxx'],
                                         y1=df1.loc[i,'miny'],y2=df1.loc[i,'maxy'])
        """
        xx1=(df1.loc[i,'minx']+df1.loc[i,'maxx'])/2-max_len/2
        xx2=(df1.loc[i,'minx']+df1.loc[i,'maxx'])/2+max_len/2
        yy1=(df1.loc[i,'miny']+df1.loc[i,'maxy'])/2-max_len/2
        yy2=(df1.loc[i,'miny']+df1.loc[i,'maxy'])/2+max_len/2

        minx, miny, maxx, maxy=cal_bound(ra=ra,leng_yan=0,x1=xx1,x2=xx2,y1=yy1,y2=yy2)


        bbox=gpd.GeoDataFrame(
            geometry=[box(minx, miny, maxx, maxy)],
            crs=counter.crs).to_crs(ccrs.PlateCarree())
        bbox_gdf = bbox.bounds

        ax3 = fig.add_axes([0.252, 0.1845, 0.362, 0.6768])
        ax3.set_xticks([])  # 隐藏x轴刻度
        ax3.set_yticks([])  # 隐藏y轴刻度
        overlay_lines = gpd.overlay(counter, bbox.to_crs(counter.crs), how='intersection')
        overlay_lines = overlay_lines.explode().reset_index(drop=True)
        overlay_lines.loc[:,"Len"]=overlay_lines.length
        overlay_lines = calculaterotation(overlay_lines)
        overlay_lines.loc[:,"type"] = overlay_lines.loc[:,'Contour']%50
        overlay_lines_cu=overlay_lines.loc[overlay_lines.loc[:,"type"]==0,:]
        overlay_lines_xi=overlay_lines.loc[overlay_lines.loc[:,"type"]!=0,:]
        overlay_lines_xi.plot(ax=ax3, linewidth=1, color='black')
        overlay_lines_cu.plot(ax=ax3, linewidth=2, color='black')

        for j in range(len(overlay_lines)):
            if overlay_lines.loc[j,'Len']>np.nanmean(overlay_lines.loc[:,'Len'])*0.05:
                ax3.text(
                    overlay_lines.loc[j,'x'],  # x坐标
                    overlay_lines.loc[j,'y'],  # y坐标
                    str(overlay_lines.loc[j,'Contour']),  # 标注文本
                    rotation=overlay_lines.loc[j,'angle'],
                    fontsize=12,  # 字体大小
                    ha='center',  # 水平对齐
                    va='center',  # 垂直对齐
                    color='orange'
                    #bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.2')  # 背景框
                )
        df1.loc[df1.index == i, :].plot(ax=ax3, linewidth=2, facecolor='none', edgecolor='red')
        ax3.set_xticks([])  # 隐藏x轴刻度
        ax3.set_yticks([])  # 隐藏y轴刻度
        ax3.text(
            x=(ax3.get_xlim()[0] + ax3.get_xlim()[1]) / 2,
            y=(ax3.get_ylim()[0] + ax3.get_ylim()[1]) / 2,
            s=str(df1.loc[i, '小班号']),
            fontsize=25,
            color='red',
            ha='center',
            weight='bold',
            path_effects=[
                path_effects.withStroke(
                    linewidth=3,  # 晕圈宽度
                    foreground='white'  # 晕圈颜色
                )
            ]
        )
        plt.xlim(minx, maxx)
        plt.ylim(miny, maxy)


        #ax4 卫星图
        ax4 = plt.axes([0.624, 0.1845, 0.362, 0.6768], projection=ccrs.Mercator())  # 左上角
        # df1.loc[df1.index==i,:].to_crs(ccrs.PlateCarree()).plot(ax=ax4, linewidth=1,facecolor='none',edgecolor='red')
        ax4.set_extent([bbox_gdf.loc[0, 'minx'], bbox_gdf.loc[0, 'maxx'], bbox_gdf.loc[0, 'miny'], bbox_gdf.loc[0, 'maxy']],
                       crs=ccrs.PlateCarree())
        ax4.add_image(tiler, 18)  # 15 是缩放级别
        ax4.add_geometries(df2.loc[df2.index == i, 'geometry'], crs=ccrs.PlateCarree(), facecolor='none', edgecolor='red',
                           linewidth=2)
        ax4.text(
            x=(ax4.get_xlim()[0] + ax4.get_xlim()[1]) / 2,
            y=(ax4.get_ylim()[0] + ax4.get_ylim()[1]) / 2,
            s=str(df1.loc[i, '小班号']),
            fontsize=25,
            color='red',
            ha='center',
            weight='bold',
            path_effects=[
                path_effects.withStroke(
                    linewidth=3,  # 晕圈宽度
                    foreground='white'  # 晕圈颜色
                )
            ]
        )
        ax4.set_xticks([])  # 隐藏x轴刻度
        ax4.set_yticks([])  # 隐藏y轴刻度


        add_north(ax3, 0.15, 0.97, line_width=1.5, text_size=0,arrow_width=0.06,arrow_height=0.06)
        add_north(ax4, 0.15, 0.97, line_width=1.5, text_size=0, arrow_width=0.06,arrow_height=0.06)
        scale_bar(ax3, x=0.02, y=0.87, w=scale*15, h=0.01)
        scale_bar(ax4, x=0.02, y=0.87, w=scale*15, h=0.01)
        guide_line(ax2,starx=df1.loc[i,'minx'],starty=df1.loc[i,'maxy'],x_pin_scale=0.95)

        ceshi = df1.loc[df1.index == 0, ['小班号', '序号', '县（区）', '乡镇（林场）', '村（分场）', '经营主体', '联系方式', '作业面积（亩）',
                                         '营林模式', '原始株数', '间伐株数', '补植株数', '保留株数', '垦复方式', '需苗量', '生物菌肥', '复合肥',
                                         '水溶肥', '实施年度']]
        ax5 = fig.add_axes([0.014, 0.0725, 0.972, 0.07])
        ax5.axis('off')  # 隐藏坐标轴
        # 创建表格数据
        cell_data = [ceshi.columns.tolist()] + ceshi.values.tolist()

        table = ax5.table(
            cellText=cell_data,
            loc='center',
            cellLoc='center',
            bbox=[0, 0, 1, 1]  # 表格占满整个axes
        )
        # 可选：设置表格样式
        table.auto_set_font_size(False)
        table.auto_set_column_width([i for i in range(len(ceshi.columns))])
        table.set_fontsize(9)
        table.scale(1, 1.5)  # 调整行高
        #plt.show()
        #plt.savefig('F:/HDY/zyj/'+str(df1.loc[i,'小班号'])+'.pdf', dpi=300, pad_inches=0,bbox_inches='tight')
        pdf.savefig(fig, dpi=300, pad_inches=0, bbox_inches='tight')
        plt.close()  # 关闭图形释放内存

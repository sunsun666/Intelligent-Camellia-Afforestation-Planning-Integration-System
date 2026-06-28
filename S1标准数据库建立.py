import arcpy
import pandas as pd
arcpy.management.CreateFeatureclass(
    out_path=r"F:\HDY\202511大样地\标准数据库构建\图斑调查数据库.gdb",
    out_name="图斑调查数据库",
    geometry_type="POLYGON",
    spatial_reference="CGCS2000 3 Degree GK CM 120E"
)
tb_filed=pd.read_excel(r'F:\HDY\202511大样地\标准数据库构建\图斑调查数据库for油茶.xlsx')
dics={'字符型':'TEXT',
      '双精度':'DOUBLE',
      '整型':'LONG',
      '浮点型':'FLOAT',}
for i in range(len(tb_filed)):
    in_table='F:/HDY/202511大样地/标准数据库构建/图斑调查数据库.gdb/图斑调查数据库'
    field_name=tb_filed.loc[i,'字段名']
    field_type=dics[tb_filed.loc[i,'数据类型']]
    field_alias=tb_filed.loc[i,'中文名']
    if field_type=='TEXT':
        field_length=tb_filed.loc[i, '长度']
        arcpy.management.AddField(in_table, field_name, field_type,
                                  field_length=str(field_length),field_alias=field_alias)
    elif field_type=='LONG':
        field_precision = tb_filed.loc[i, '长度']
        field_scale=''
        field_length=''
        arcpy.management.AddField(in_table, field_name, field_type,
                                  field_precision=str(int(field_precision)),field_alias=field_alias)
    else:
        field_precision = tb_filed.loc[i, '长度']
        field_scale=tb_filed.loc[i,'小数位']
        field_length=''
        arcpy.management.AddField(in_table, field_name, field_type,
                                  field_precision=str(int(field_precision)),field_scale=str(field_scale),
                                  field_alias=field_alias)
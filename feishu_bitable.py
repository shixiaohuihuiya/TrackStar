from baseopensdk import BaseClient, JSON
from baseopensdk.api.base.v1 import *
import logging
import json
class feishu_bitable():
    def __init__(self, personal_base_token, feishu_bitable_url):
        self.personal_base_token = personal_base_token
        self.feishu_bitable_url = feishu_bitable_url
        self.feishu_bitable_app_token = feishu_bitable_url.split('/')[4].split('?')[0]
        self.feishu_bitable_table_id = feishu_bitable_url[feishu_bitable_url.find('table=') + len('table=') : feishu_bitable_url.find('&')]
        self.bitable_view = feishu_bitable_url.split('view=')[1]
        self.bitable_view_name = '点赞总表'
        self.bitable_view_clone_name = '最近一日'
        self.bitable_view_clone_filter_condition = "Today"
        self.default_view_fields = [
            {'name': '姓名', 'type': 1},
            {'name': '用户主页', 'type': 1},
            {'name': '位置', 'type':1},
            {'name': '简介', 'type':1},
            {'name': '公开仓库数', 'type':1},
            {'name': '公开Gist数', 'type':1},
            {'name': '关注者数', 'type':1},
            {'name': '关注数', 'type':1},
            {'name': '评分', 'type':1},
            {'name': '创建时间', 'type':5},
            {'name': '更新时间', 'type':5},
            {'name': '收集时间', 'type':5}
        ]

    # 构建客户端
    def build_client(self):
        client: BaseClient = BaseClient.builder() \
                .app_token(self.feishu_bitable_app_token) \
                .personal_base_token(self.personal_base_token) \
                .build()
        return client

    # 获取视图
    def get_all_view(self, table_id):
        request = ListAppTableViewRequest.builder() \
            .table_id(table_id) \
            .build()
        response = self.build_client().base.v1.app_table_view.list(request)
        return response.data.items

    # 更新视图
    def patch_view(self, view_id, table_id, view_name, view_field_id, conjunction,operator,view_field_filter):
        
        if operator and view_field_filter:
            view_filter = f'["{view_field_filter}"]'
            view_field_filter_condition = AppTableViewPropertyFilterInfoCondition().builder() \
                .field_id(view_field_id) \
                .operator(operator) \
                .value(view_filter) \
                .build()

            filter_info = AppTableViewPropertyFilterInfo().builder() \
                .conjunction(conjunction) \
                .conditions([view_field_filter_condition]) \
                .build()
        
            view_property = AppTableViewProperty().builder() \
                .filter_info(filter_info) \
                .build()
        
            view_body = PatchAppTableViewRequestBody().builder() \
                .view_name(None) \
                .property(view_property) \
                .build()

            request = PatchAppTableViewRequest.builder() \
                .table_id(table_id) \
                .view_id(view_id) \
                .request_body(view_body) \
                .build()        
        else:
            view_body = PatchAppTableViewRequestBody().builder() \
                .view_name(view_name) \
                .build()
            request = PatchAppTableViewRequest.builder() \
                .table_id(table_id) \
                .view_id(view_id) \
                .request_body(view_body) \
                .build()
        response = self.build_client().base.v1.app_table_view.patch(request)
        logging.info("更新视图的id日志：", "success" if response.msg == "success" else "更新失败")
    
    # 获取所有的字段信息
    def get_all_fields(self, table_id,view_id):
        request = ListAppTableFieldRequest.builder() \
            .table_id(table_id) \
            .view_id(view_id) \
            .build()
        response = self.build_client().base.v1.app_table_field.list(request)
        return response.data.items

    # 跟新字段信息
    def update_field(self, field_id, field_name, field_type):
        app_table_field = AppTableField().builder() \
            .field_name(field_name) \
            .type(field_type) \
            .build()
        
        request = UpdateAppTableFieldRequest.builder() \
            .table_id(self.feishu_bitable_table_id) \
            .field_id(field_id) \
            .request_body(app_table_field) \
            .build()
        response = self.build_client().base.v1.app_table_field.update(request)
        logging.info(response.msg) 
    
    # 获取所有记录的id
    def get_all_records(self, table_id, view_id):
        request = ListAppTableRecordRequest.builder() \
            .table_id(table_id) \
            .view_id(view_id) \
            .build()
        response = self.build_client().base.v1.app_table_record.list(request)
        return response.data.items

    # 删除视图的所有记录
    def delete_view_records(self, table_id, view_id):
        records = self.get_all_records(table_id, view_id)
        for record in records:
            request = DeleteAppTableRecordRequest.builder() \
                .table_id(table_id) \
                .record_id(record.record_id) \
                .build()
            response = self.build_client().base.v1.app_table_record.delete(request)
            logging.info(response.msg)

    # 删除所有字段
    def delete_all_fields(self, table_id, view_id):
        # 获取所有的字段信息
        field_ids = [field.field_id for field in self.get_all_fields(table_id, view_id)]
        
        for field_id in field_ids:
            request = DeleteAppTableFieldRequest.builder() \
                .table_id(table_id) \
                .field_id(field_id) \
                .build()
            response = self.build_client().base.v1.app_table_field.delete(request)
            logging.info("删除所有字段的id日志：", response.msg)
    
    # 创建所有字段
    def create_fields(self, table_id, view_fields):

        for field in view_fields:
           
           app_table_field = AppTableField().builder() \
               .field_name(field['name']) \
               .type(field['type']) \
               .build()
           
           request = CreateAppTableFieldRequest.builder() \
               .table_id(table_id) \
               .request_body(app_table_field) \
               .build()
           response = self.build_client().base.v1.app_table_field.create(request)
           logging.info("创建所有字段的id日志：", response.msg)

    # 创建视图
    def create_view(self, view_name, view_type, table_id):
        view_body = ReqView().builder() \
            .view_name(view_name) \
            .view_type(view_type) \
            .build()
        
        request = CreateAppTableViewRequest.builder() \
            .table_id(table_id) \
            .request_body(view_body) \
            .build()
        response = self.build_client().base.v1.app_table_view.create(request)
        logging.info("创建视图的id日志：", response.msg)
        return response.data.view.view_id
    
    # 批量新增记录
    def batch_create_records(self, records):
        print(111111111111111111111111)
      

        batch_create_app_table_record_request_body = BatchCreateAppTableRecordRequestBody().builder() \
            .records(records) \
            .build()
        
        request = BatchCreateAppTableRecordRequest.builder() \
            .table_id(self.feishu_bitable_table_id) \
            .request_body(batch_create_app_table_record_request_body) \
            .build()
        response = self.build_client().base.v1.app_table_record.create(request)
        if response.msg == "success":
            logging.info("批量新增记录成功：%s", response.__dict__)
        else:
            logging.error("批量新增记录失败：%s", response.__dict__)
        
    
     # 获取特定名称的视图id
    def get_one_view_id(self, view_name):
        view_info = self.get_all_view(self.feishu_bitable_table_id)
        for view in view_info:
            if view.view_name == view_name:
                return view.view_id
        return None
    
    # 初始化视图
    def init_view(self):
        table_id = self.feishu_bitable_table_id
        view_name = self.bitable_view_name
        view_clone_name = self.bitable_view_clone_name
        view_type = "grid"
        view_default_id = self.bitable_view
        view_default_field = self.default_view_fields
        view_field_filter = self.bitable_view_clone_filter_condition
        conjunction = "and"
        operator = "is"
        # 1.修改视图的名称
        self.patch_view(
            view_default_id, 
            table_id, 
            view_name, 
            None, 
            None, 
            None, 
            None
            )
        # 2.修改索引名称
        self.update_field(view_default_id, view_name, view_default_field)
        # 3.删除视图记录
        self.delete_view_records(table_id, view_default_id)
        # 4.删除所有字段
        self.delete_all_fields(table_id, view_default_id)
        # 5.创建所有字段
        self.create_fields(table_id, view_default_field)
        # 6.创建视图
        create_view_id = self.create_view(view_clone_name, view_type, table_id)
        # 7.设置过滤条件
        response = self.patch_view(
            create_view_id, 
            table_id,
            view_name,
            [field.field_id for field in self.get_all_fields(table_id, create_view_id)][-1],
            conjunction,
            operator,
            view_field_filter
            )

    # 判断视图是否存在
    def is_view_exist(self, view_name):
        print(self.feishu_bitable_table_id)
        print(view_name)
        # 查询view名字是否存在
        response = self.get_all_view(self.feishu_bitable_table_id)
        for view in response:
            if view.view_name == view_name:
                return True
        return False

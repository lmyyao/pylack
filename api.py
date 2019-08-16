import requests
from pprint import pprint as print


class LackAPIException(Exception):
    pass


def get_token_first(func):
    def new_func(self, *args, **kwargs):
        _ = self.token
        return func(self, *args, **kwargs)

    return new_func


def get_own_department_first(func):
    def new_func(self, *args, **kwargs):
        department_id = self.own_department
        if department_id is None:
            raise LackAPIException(
                "you must overwrite get_own_department method")
        return func(self, *args, **kwargs)

    return new_func


class LackAPI(object):
    _app_access_token = None
    _own_department_id = None

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret

    def _get_token(self):
        uri = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/"
        response = requests.post(uri,
                                 json={
                                     "app_id": self.app_id,
                                     "app_secret": self.app_secret
                                 })
        self._app_access_token = response.json()["app_access_token"]

    @property
    def token(self):
        if self._app_access_token is None:
            self._get_token()
        return self._app_access_token

    def get_headers(self):
        return {"Authorization": "Bearer {}".format(self.token)}

    @get_token_first
    def get_auth_departments(self):
        uri = "https://open.feishu.cn/open-apis/contact/v1/scope/get"
        return requests.get(uri, headers=self.get_headers()).json()

    @get_token_first
    def get_chats(self, page=1, page_size=100):
        uri = f"https://open.feishu.cn/open-apis/chat/v3/list?page={page}&page_size={page_size}"
        return requests.get(uri, headers=self.get_headers()).json()

    @get_token_first
    def get_department_info(self, department_id):
        uri = f"https://open.feishu.cn/open-apis/contact/v1/department/info/get?department_id={department_id}"
        return requests.get(uri, headers=self.get_headers()).json()

    @get_token_first
    def get_department_users(self, department_id, page_size=100, offset=0):
        uri = f"https://open.feishu.cn/open-apis/contact/v1/department/user/list?department_id={department_id}&page_size={page_size}&offset={offset}&fetch_child=true"
        return requests.get(uri, headers=self.get_headers()).json()

    @property
    def own_department(self):
        if self._own_department_id is None:
            self.get_own_department()
        return self._own_department_id

    def get_own_department(self):
        department_id = self.get_auth_departments(
        )["data"]["authed_departments"][0]
        self.set_own_department(department_id)

    def set_own_department(self, department_id):
        self._own_department_id = department_id

    @get_token_first
    @get_own_department_first
    def get_own_deparment_info(self):
        return self.get_department_info(self._own_department_id)

    @get_token_first
    @get_own_department_first
    def get_own_department_users(self, page_size=100, offset=0):
        return self.get_department_users(self._own_department_id,
                                         page_size=page_size,
                                         offset=offset)

    
    @get_token_first
    @get_own_department_first
    def get_own_department_user_by_name(self, name):
        users = self.get_own_department_users()
        for user in users["data"]["user_list"]:
            if user["name"] == name:
                return user
        return {}

    @get_token_first
    def get_user_detail(self, openid):
        uri = f"https://open.feishu.cn/open-apis/contact/v1/user/batch_get?open_ids={openid}"
        return requests.get(uri, headers=self.get_headers()).json()

    @get_token_first
    @get_own_department_first
    def get_own_deparment_user_detail_by_name(self, name):
        user = self.get_own_department_user_by_name(name)
        if user:
            return self.get_user_detail(user["open_id"])
        return {}
    
if __name__ == "__main__":
    pass

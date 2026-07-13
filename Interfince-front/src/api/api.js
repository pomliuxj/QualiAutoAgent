import axios from 'axios';


// export const test = 'http://120.27.209.105:19000';
export const test = 'http://127.0.0.1:8000';

//  调试接口
export const testApi = (headers, params) => {
    return axios.post(`${test}/api/api/fast_test`, params, {headers}).then(res => res.data); };
// 注册
export const register = params => {
    return axios.post(`${test}/api/user/register`, params).then(res => res.data); };
// 登录
export const requestLogin = params => {
    return axios.post(`${test}/api/user/login`, params).then(res => res.data); };
// 记录访客
export const recordVisitor = params => {
    return axios.post(`${test}/api/user/VisitorRecord`, params).then(res => res.data); };
// 获取项目
export const getProject = (headers, params) => {
    return axios.get(`${test}/api/project/projection`, { params: params, headers:headers}).then(res => res.data); };
// 删除项目
export const delProject = (headers, params) => {
    return axios.delete(`${test}/api/project/projection`, {data:params,headers}).then(res => res.data); };
// 禁用项目
export const disableProject = (headers, params) => {
    return axios.post(`${test}/api/project/disable_project`, params, {headers}).then(res => res.data); };
// 启用项目
export const enableProject = (headers, params) => {
    return axios.post(`${test}/api/project/enable_project`, params, {headers}).then(res => res.data); };
// 修改项目
export const updateProject = (headers, params) => {
    return axios.put(`${test}/api/project/projection`, params, {headers}).then(res => res.data); };
// 添加项目
export const addProject = (headers, params) => {
    return axios.post(`${test}/api/project/projection`, params, {headers}).then(res => res.data); };
// 获取项目详情
export const getProjectDetail = (headers, params) => {
    return axios.get(`${test}/api/title/project_info`, { params: params, headers:headers}).then(res => res.data); };
// 获取测试地址列表
export const getHost = (headers, params) => {
    return axios.get(`${test}/api/global/host_total`, { params: params, headers:headers}).then(res => res.data); };
// 删除测试地址列表
export const delHost = (headers, params) => {
    return axios.delete(`${test}/api/global/host_total`, {data:params, headers}).then(res => res.data); };
// 禁用测试地址列表
export const disableHost = (headers, params) => {
    return axios.post(`${test}/api/global/disable_host`, params, {headers}).then(res => res.data); };
// 启用测试地址列表
export const enableHost = (headers, params) => {
    return axios.post(`${test}/api/global/enable_host`, params, {headers}).then(res => res.data); };
// 修改测试地址列表
export const updateHost = (headers, params) => {
    return axios.put(`${test}/api/global/host_total`, params, {headers}).then(res => res.data); };
// 添加测试地址列表
export const addHost = (headers, params) => {
    return axios.post(`${test}/api/global/host_total`, params, {headers}).then(res => res.data); };
// 获取项目动态
export const getProjectDynamicList = (headers, params) => {
    return axios.get(`${test}/api/dynamic/dynamic`, { params: params, headers:headers}).then(res => res.data); };
// 获取项目成员
export const getProjectMemberList = (headers, params) => {
    return axios.get(`${test}/api/member/project_member`, { params: params, headers:headers}).then(res => res.data); };
// 获取发送邮件配置
export const getEmailConfigDetail = (headers, params) => {
    return axios.get(`${test}/api/member/get_email`, { params: params, headers:headers}).then(res => res.data); };
// 删除邮件配置
export const delEmailConfig = (headers, params) => {
    return axios.post(`${test}/api/member/del_email`, params, {headers}).then(res => res.data); };
// 添加邮件配置
export const addEmailConfig = (headers, params) => {
    return axios.post(`${test}/api/member/email_config`, params, {headers}).then(res => res.data); };
// 添加项目成员
export const addProjectMember = (headers, params) => {
    return axios.post(`${test}/api/member/add_member`, params, {headers}).then(res => res.data); };
// 移除项目成员
export const removeProjectMember = (headers, params) => {
    return axios.post(`${test}/api/member/remove_member`, params, {headers}).then(res => res.data); };
// 修改成员角色
export const updateMemberRole = (headers, params) => {
    return axios.put(`${test}/api/member/update_role`, params, {headers}).then(res => res.data); };
// 用户列表（超管用，搜索用户）
export const getUserList = (headers, params) => {
    return axios.get(`${test}/api/account/user_list`, { params: params, headers:headers}).then(res => res.data); };
// 获取自动化测试结果
export const getTestResultList = (headers, params) => {
    return axios.get(`${test}/api/report/auto_test_report`, { params: params, headers:headers}).then(res => res.data); };
// 获取最近10次测试时间
export const getTestTenTime = (headers, params) => {
    return axios.get(`${test}/api/report/test_time`, { params: params, headers:headers}).then(res => res.data); };
// 获取最近10次测试比例结果
export const getTestTenResult = (headers, params) => {
    return axios.get(`${test}/api/report/lately_ten`, { params: params, headers:headers}).then(res => res.data); };
// 添加接口
export const addApiDetail = (headers, params) => {
    return axios.post(`${test}/api/api/add_api`, params, {headers}).then(res => res.data); };
// 获取接口分组列表
export const getApiGroupList = (headers, params) => {
    return axios.get(`${test}/api/api/group`, { params: params, headers:headers}).then(res => res.data); };
// 添加接口分组
export const addApiGroup = (headers, params) => { return axios.post(`${test}/api/api/add_group`, params, {headers}).then(res => res.data); };
// 修改接口分组
export const updateApiGroup = (headers, params) => {
    return axios.post(`${test}/api/api/update_name_group`, params, {headers}).then(res => res.data); };
// 删除接口分组
export const delApiGroup = (headers, params) => {
    return axios.post(`${test}/api/api/del_group`, params, {headers}).then(res => res.data); };
//新增定时任务接口
export const addTask = (headers, params) => {
    return axios.post(`${test}/api/automation/TaskInfo`, params, {headers}).then(res => res.data); };
//查询定时任务接口
export const seachTask = (headers, params) => {
    return axios.get(`${test}/api/automation/TaskInfo`, { params: params, headers:headers}).then(res => res.data)};
//删除定时任务接口
export const delTask = (headers, params) => {
    return axios.delete(`${test}/api/automation/TaskInfo`, { data: params, headers}).then(res => res.data)};
//修改定时任务接口
export const updateTask = (headers, params) => {
    return axios.put(`${test}/api/automation/TaskInfo`,params, { headers:headers}).then(res => res.data)};
//查询CASE组接口
export const getCase = (headers, params) => {
    return axios.get(`${test}/api/automation/case_list`, { params: params, headers}).then(res => res.data)};
//查询定时任务执行记录接口
export const TaskRecode = (headers, params) => {
    return axios.get(`${test}/api/automation/TaskRecode`, { params: params, headers}).then(res => res.data)};
//查询全局变量
export const GetVariables = (headers,params) => {
    return axios.get(`${test}/api/global/global_variables`, { params:params, headers}).then(res => res.data)};
//运行全局变量
export const RunVariables = (headers, params) => {
    return axios.post(`${test}/api/global/global_variables`, params, {headers}).then(res => res.data); };
//创建全局变量
export const CreateVariables = (headers, params) => {
    return axios.put(`${test}/api/global/global_variables`, params, {headers}).then(res => res.data); };
//修改全局变量
export const UpdateVariables = (headers, params) => {
    return axios.delete(`${test}/api/global/global_variables`, { data: params, headers}).then(res => res.data); };
//查询数据源
export const GetDataBase = (headers,params) => {
    return axios.get(`${test}/api/global/global_database`, { params:params, headers}).then(res => res.data)};
//新增数据源
export const CreateDataBase = (headers, params) => {
    return axios.post(`${test}/api/global/global_database`, params, {headers}).then(res => res.data); };
//修改数据源
export const UpdateDataBase = (headers, params) => {
    return axios.put(`${test}/api/global/global_database`, params, {headers}).then(res => res.data); };
//删除数据源
export const DeleteDataBase = (headers, params) => {
    return axios.delete(`${test}/api/global/global_database`, { data: params, headers}).then(res => res.data); };
//检验数据源可用
export const CheckDataBase = (headers, params) => {
    return axios.post(`${test}/api/global/global_checkdatabase`, params, {headers}).then(res => res.data); };
//新增数据库校验
export const Createcasedatabase = (headers, params) => {
    return axios.post(`${test}/api/automation/global_casedatabasecheck`, params, {headers}).then(res => res.data); };
//修改数据库校验
export const Updatecasedatabase = (headers, params) => {
    return axios.put(`${test}/api/automation/global_casedatabasecheck`, params, {headers}).then(res => res.data); };
//删除数据库校验
export const Deletecasedatabase = (headers, params) => {
    return axios.delete(`${test}/api/automation/global_casedatabasecheck`, { data: params, headers}).then(res => res.data); };
//数据库校验列表
export const Getcasedatabase = (headers, params) => {
    return axios.get(`${test}/api/automation/global_casedatabasecheck`, params, {headers}).then(res => res.data); };
//测试数据库sql
export const Testruncasedata = (headers, params) => {
    return axios.post(`${test}/api/automation/global_testrundatacase`, params, {headers}).then(res => res.data); };
// AI 自动生成测试用例 SSE 接口
export const aiTestCase = `http://127.0.0.1:9000/api/chat/test_case`;

export const staticdata={
    request: [{value: 'GET', label: 'GET'},
            {value: 'POST', label: 'POST'},
            {value: 'PUT', label: 'PUT'},
            {value: 'DELETE', label: 'DELETE'},
            {value: 'DUBBO', label: 'DUBBO'}
            ],
    Http: [{value: 'HTTP', label: 'HTTP'},
            {value: 'HTTPS', label: 'HTTPS'},
            {value: 'DUBBO', label: 'DUBBO'}],
    paramTyep: [{value: 'Int', label: 'Int'},
                {value: 'String', label: 'String'}],
    header: [{value: 'Accept', label: 'Accept'},
            {value: 'Accept-Charset', label: 'Accept-Charset'},
            {value: 'Accept-Encoding', label: 'Accept-Encoding'},
            {value: 'Accept-Language', label: 'Accept-Language'},
            {value: 'Accept-Ranges', label: 'Accept-Ranges'},
            {value: 'Authorization', label: 'Authorization'},
            {value: 'Cache-Control', label: 'Cache-Control'},
            {value: 'Connection', label: 'Connection'},
            {value: 'Cookie', label: 'Cookie'},
            {value: 'Content-Length', label: 'Content-Length'},
            {value: 'Content-Type', label: 'Content-Type'},
            {value: 'Content-MD5', label: 'Content-MD5'},
            {value: 'Date', label: 'Date'},
            {value: 'Expect', label: 'Expect'},
            {value: 'From', label: 'From'},
            {value: 'Host', label: 'Host'},
            {value: 'If-Match', label: 'If-Match'},
            {value: 'If-Modified-Since', label: 'If-Modified-Since'},
            {value: 'If-None-Match', label: 'If-None-Match'},
            {value: 'If-Range', label: 'If-Range'},
            {value: 'If-Unmodified-Since', label: 'If-Unmodified-Since'},
            {value: 'Max-Forwards', label: 'Max-Forwards'},
            {value: 'Origin', label: 'Origin'},
            {value: 'Pragma', label: 'Pragma'},
            {value: 'Proxy-Authorization', label: 'Proxy-Authorization'},
            {value: 'Range', label: 'Range'},
            {value: 'Referer', label: 'Referer'},
            {value: 'TE', label: 'TE'},
            {value: 'Upgrade', label: 'Upgrade'},
            {value: 'User-Agent', label: 'User-Agent'},
            {value: 'Via', label: 'Via'},
            {value: 'Warning', label: 'Warning'}],
    httpCode:[{value: '', label: ''},
            {value: '200', label: '200'},
            {value: '404', label: '404'},
            {value: '400', label: '400'},
            {value: '500', label: '500'},
            {value: '502', label: '502'},
            {value: '302', label: '302'}],
   jsonType:[{value: 'gte', label: '大于'},
            {value: 'lte', label: '小于'},
            {value: 'equal', label: '等于'},
            {value: 'contain', label: '包含'},
            {value: 'notNull', label: '不为空'},
    ]
}
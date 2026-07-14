<template>
  <section>
    <el-row :span="24" class="row-title">
      <el-col :span="4" v-if="showSidebar">
        <el-button class="addGroup" @click="handleAddGroup">新增分组</el-button>
        <div class="group-title"><strong>用例分组</strong></div>
        <div class="group-title" style="cursor:pointer;">
          <router-link :to="{ name: '用例列表', params: {project_id: this.$route.params.project_id}}" style="text-decoration: none; color: aliceblue;">
            所有用例
          </router-link>
        </div>
        <aside>
          <el-menu default-active="2" class="el-menu-vertical-demo" active-text-color="rgb(32, 160, 255)" :unique-opened="true">
            <template v-for="(item, index) in groupData">
              <router-link :to="{ name: '分组用例列表', params: {project_id: project, firstGroup: item.id}}" style="text-decoration:none;">
                <el-menu-item :index="index+''" :key="item.id" class="group">
                  <template slot="title">{{ item.name }}
                    <el-dropdown trigger="hover" class="editGroup" style="margin-right:10%">
                      <i class="el-icon-more"></i>
                      <el-dropdown-menu slot="dropdown">
                        <el-dropdown-item @click.native="handleDelGroup(item.id)">删除</el-dropdown-item>
                        <el-dropdown-item @click.native="handleEditGroup(item.id, item.name)">修改</el-dropdown-item>
                      </el-dropdown-menu>
                    </el-dropdown>
                  </template>
                </el-menu-item>
              </router-link>
            </template>
          </el-menu>
        </aside>
      </el-col>

      <!-- 新增分组 dialog -->
      <el-dialog title="新增用例分组" :visible.sync="addGroupFormVisible" :close-on-click-modal="false" style="width: 60%; left: 20%">
        <el-form :model="addGroupForm" label-width="80px" :rules="addGroupFormRules" ref="addGroupForm">
          <el-form-item label="分组名称" prop="name">
            <el-input v-model.trim="addGroupForm.name" auto-complete="off" style="width: 90%"></el-input>
          </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click.native="addGroupFormVisible = false">取消</el-button>
          <el-button type="primary" @click.native="addGroupSubmit" :loading="addGroupLoading">提交</el-button>
        </div>
      </el-dialog>

      <!-- 编辑分组 dialog -->
      <el-dialog title="编辑用例分组" :visible.sync="editGroupFormVisible" :close-on-click-modal="false" style="width: 60%; left: 20%">
        <el-form :model="editGroupForm" label-width="80px" :rules="editGroupFormRules" ref="editGroupForm">
          <el-form-item label="分组名称" prop="name">
            <el-input v-model.trim="editGroupForm.name" auto-complete="off"></el-input>
          </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click.native="editGroupFormVisible = false">取消</el-button>
          <el-button type="primary" @click.native="editGroupSubmit" :loading="editGroupLoading">提交</el-button>
        </div>
      </el-dialog>

      <el-col :span="showSidebar ? 20 : 24">
        <div style="margin-left: 10px; margin-right: 20px">
          <router-view></router-view>
        </div>
      </el-col>
    </el-row>
  </section>
</template>

<script>
import { test } from '../../../api/api'
import $ from 'jquery'

export default {
  data() {
    return {
      project: '',
      groupData: [],
      addGroupFormVisible: false,
      addGroupLoading: false,
      addGroupFormRules: {
        name: [
          { required: true, message: '请输入分组名称', trigger: 'blur' },
        ]
      },
      addGroupForm: {
        name: '',
      },
      editGroupFormVisible: false,
      editGroupLoading: false,
      editGroupFormRules: {
        name: [
          { required: true, message: '请输入分组名称', trigger: 'blur' },
        ]
      },
      editGroupForm: {
        name: '',
        id: '',
      },
    }
  },
  computed: {
    showSidebar() {
      return !['用例接口列表', '添加新接口', '修改接口', '测试报告', 'AI生成用例'].includes(this.$route.name)
    },
  },
  methods: {
    getCaseGroup() {
      let self = this
      $.ajax({
        type: 'get',
        url: test + '/api/automation/group',
        async: true,
        data: { project_id: this.$route.params.project_id },
        headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) },
        timeout: 5000,
        success: function (data) {
          if (data.code === '999999') {
            self.groupData = data.data
          } else {
            self.$message.error({ message: data.msg, center: true })
          }
        }
      })
    },
    handleAddGroup() {
      this.addGroupForm.name = ''
      this.addGroupFormVisible = true
    },
    handleEditGroup(id, name) {
      this.editGroupForm.id = id
      this.editGroupForm.name = name
      this.editGroupFormVisible = true
    },
    addGroupSubmit() {
      this.$refs.addGroupForm.validate((valid) => {
        if (valid) {
          let self = this
          this.$confirm('确认提交吗？', '提示', {}).then(() => {
            self.addGroupLoading = true
            $.ajax({
              type: 'post',
              url: test + '/api/automation/add_group',
              async: true,
              data: JSON.stringify({
                project_id: Number(this.$route.params.project_id),
                name: self.addGroupForm.name
              }),
              headers: {
                'Content-Type': 'application/json',
                Authorization: 'Token ' + JSON.parse(localStorage.getItem('token'))
              },
              timeout: 5000,
              success: function (data) {
                self.addGroupLoading = false
                if (data.code === '999999') {
                  self.$message({ message: '添加成功', center: true, type: 'success' })
                  self.$refs['addGroupForm'].resetFields()
                  self.addGroupFormVisible = false
                  self.getCaseGroup()
                } else {
                  self.$message.error({ message: data.msg, center: true })
                }
              }
            })
          })
        }
      })
    },
    editGroupSubmit() {
      this.$refs.editGroupForm.validate((valid) => {
        if (valid) {
          let self = this
          this.$confirm('确认提交吗？', '提示', {}).then(() => {
            self.editGroupLoading = true
            $.ajax({
              type: 'post',
              url: test + '/api/automation/update_name_group',
              async: true,
              data: JSON.stringify({
                project_id: Number(this.$route.params.project_id),
                id: Number(self.editGroupForm.id),
                name: self.editGroupForm.name
              }),
              headers: {
                'Content-Type': 'application/json',
                Authorization: 'Token ' + JSON.parse(localStorage.getItem('token'))
              },
              timeout: 5000,
              success: function (data) {
                self.editGroupLoading = false
                if (data.code === '999999') {
                  self.$message({ message: '修改成功', center: true, type: 'success' })
                  self.$refs['editGroupForm'].resetFields()
                  self.editGroupFormVisible = false
                  self.getCaseGroup()
                } else {
                  self.$message.error({ message: data.msg, center: true })
                }
              }
            })
          })
        }
      })
    },
    handleDelGroup(id) {
      this.$confirm('确认删除该分组吗？分组下的用例不会被删除。', '提示', { type: 'warning' }).then(() => {
        let self = this
        $.ajax({
          type: 'post',
          url: test + '/api/automation/del_group',
          async: true,
          data: JSON.stringify({
            project_id: Number(this.$route.params.project_id),
            id: Number(id)
          }),
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Token ' + JSON.parse(localStorage.getItem('token'))
          },
          timeout: 5000,
          success: function (data) {
            if (data.code === '999999') {
              self.$message({ message: '删除成功', center: true, type: 'success' })
              self.getCaseGroup()
            } else {
              self.$message.error({ message: data.msg, center: true })
            }
          }
        })
      }).catch(() => {})
    },
  },
  mounted() {
    this.getCaseGroup()
    this.project = this.$route.params.project_id
  }
}
</script>

<style lang="scss" scoped>
.group-title {
  padding: 14px 10px;
  margin: 0;
  text-align: center;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  background-color: #1d4ed8;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  letter-spacing: 0.02em;
}
.group .editGroup {
  float: right;
  opacity: 0.5;
  transition: opacity 0.15s ease;
}
.group:hover .editGroup {
  opacity: 1;
}
.row-title {
  margin: 24px 28px;
}
.addGroup {
  margin-top: 0;
  margin-bottom: 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.15s ease;
}
</style>

<!-- Global dropdown polish -->
<style lang="scss">
.group .editGroup .el-dropdown-menu {
  border-radius: 8px;
  padding: 4px;
  border: 1px solid #e8eaed;
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.06),
    0 10px 15px -3px rgba(0, 0, 0, 0.08);

  .el-dropdown-menu__item {
    border-radius: 6px;
    margin: 2px;
    padding: 8px 14px;
    font-size: 13px;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    font-weight: 450;
    transition: all 0.15s ease;

    &:hover {
      background: #f0f5ff;
      color: #1677ff;
    }
  }
}
</style>

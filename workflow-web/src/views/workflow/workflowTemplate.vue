<template>
  <div class="app-container">
    <el-button
      @click="dialogFormVisible = true"
      type="primary">
      Add New Workflow Template
    </el-button>
    <el-table
      v-loading="listLoading"
      :data="list"
      element-loading-text="Loading"
      border
      fit
      highlight-current-row>
      <el-table-column align="center" label="ID" width="95">
        <template slot-scope="scope">
          {{ scope.$index }}
        </template>
      </el-table-column>
      <el-table-column label="Name">
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column align="center" prop="created_at" label="ctime" width="200">
        <template slot-scope="scope">
          <span>{{ scope.row._ctime }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" prop="created_at" label="mtime" width="200">
        <template slot-scope="scope">
          <span>{{ scope.row._mtime }}</span>
        </template>
      </el-table-column>
      <el-table-column
      fixed="right"
      label="Handle"
      width="100">
        <template slot-scope="scope">
          <el-button
            @click="jump2EditPage(scope.row.id)"
            type="text"
            size="small">
            Edit
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      background
      v-model="page"
      layout="prev, pager, next"
      :total="count">
    </el-pagination>
    <el-dialog title="New Workflow Template" :visible.sync="dialogFormVisible">
      <el-form :model="form">
        <el-form-item label="Name" :label-width="formLabelWidth">
          <el-input v-model="form.name" autocomplete="off"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="addData">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getWorkflowTemplate, addWorkflowTemplate } from '@/api/workflow'

export default {
  name: 'workflowTemplate',
  filters: {
    statusFilter(status) {
      const statusMap = {
        published: 'success',
        draft: 'gray',
        deleted: 'danger'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      form:{},
      formLabelWidth:'120px',
      dialogFormVisible: false,
      list: null,
      page:1,
      count:0,
      listLoading: true
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      this.listLoading = true
      getWorkflowTemplate(this.listQuery).then(response => {
        this.list = response.results
        this.count = response.count
        this.listLoading = false
      })
    },
    addData() {
      addWorkflowTemplate(this.form)
        .then(
          response => {
            this.dialogFormVisible = false
            this.fetchData()
          }
        )
        .catch(
          e => {
            console.log(e)
          }
        )
    },
    jump2EditPage(id){
      this.$router.push(
        {
            path: 'workflowDefine',
            name: 'workflowDefine',
            params: {
                id: id
            }
        }
      )
    }
  }
}
</script>

<template>
    <section class="test-report-container">
        <!-- 头部区域：返回按钮 + KPI卡片 -->
        <div class="report-header">
            <el-button class="return-list" @click="back">
                <i class="el-icon-arrow-left" style="margin-right: 5px"></i>返回用例列表
            </el-button>
            <div class="stats-cards">
                <div class="stat-card stat-pass">
                    <div class="stat-value">{{pass}}</div>
                    <div class="stat-label">通过</div>
                </div>
                <div class="stat-card stat-fail">
                    <div class="stat-value">{{fail}}</div>
                    <div class="stat-label">失败</div>
                </div>
                <div class="stat-card stat-error">
                    <div class="stat-value">{{error}}</div>
                    <div class="stat-label">错误</div>
                </div>
                <div class="stat-card stat-total">
                    <div class="stat-value">{{total}}</div>
                    <div class="stat-label">总计</div>
                </div>
            </div>
        </div>

        <!-- 图表区域 -->
        <div class="chart-row">
            <el-row :gutter="20">
                <el-col :xs="24" :sm="24" :md="12" :lg="12">
                    <div class="chart-card">
                        <div class="chart-title">
                            <i class="el-icon-pie-chart"></i> 测试结果分布
                        </div>
                        <div ref="pieChart" class="echarts-chart"></div>
                    </div>
                </el-col>
                <el-col :xs="24" :sm="24" :md="12" :lg="12">
                    <div class="chart-card">
                        <div class="chart-title">
                            <i class="el-icon-data-line"></i> 测试执行统计
                        </div>
                        <div ref="barChart" class="echarts-chart"></div>
                    </div>
                </el-col>
            </el-row>
        </div>

        <!-- 测试结果表格 -->
        <div class="table-container">
            <el-table
                :data="tableData"
                v-loading="listLoading"
                :row-style="tableRowStyle"
                @expand-change="showJson"
                class="test-result-table"
                header-row-class-name="table-header-class"
                stripe
                border>
                <el-table-column type="expand">
                    <template slot-scope="props">
                        <div class="expand-content">
                            <el-form label-position="left" class="demo-table-expand">
                                <el-row :gutter="20">
                                    <el-col :span="12">
                                        <el-form-item label="接口名称">
                                            <span class="form-value">{{ props.row.name }}</span>
                                        </el-form-item>
                                    </el-col>
                                    <el-col :span="12">
                                        <el-form-item label="测试环境">
                                            <span class="form-value">{{ props.row.host }}</span>
                                        </el-form-item>
                                    </el-col>
                                </el-row>
                                <el-row :gutter="20">
                                    <el-col :span="12">
                                        <el-form-item label="接口地址">
                                            <span class="form-value api-url">{{ props.row.apiAddress }}</span>
                                        </el-form-item>
                                    </el-col>
                                    <el-col :span="12">
                                        <el-form-item label="请求方式">
                                            <el-tag :type="getRequestTypeTag(props.row.requestType)" size="small">{{ props.row.requestType }}</el-tag>
                                        </el-form-item>
                                    </el-col>
                                </el-row>
                                <el-row :gutter="20">
                                    <el-col :span="12">
                                        <el-form-item label="校验方式">
                                            <el-tag :type="getExamineTypeTag(props.row.examineType)" size="small">{{ getExamineTypeText(props.row.examineType) }}</el-tag>
                                        </el-form-item>
                                    </el-col>
                                    <el-col :span="12">
                                        <el-form-item label="测试结果">
                                            <el-tag :type="getResultTag(props.row.result)" size="medium" effect="dark">{{ props.row.result || 'NotRun' }}</el-tag>
                                        </el-form-item>
                                    </el-col>
                                </el-row>
                                <el-row :gutter="20">
                                    <el-col :span="24">
                                        <el-form-item label="测试时间">
                                            <span class="form-value"><i class="el-icon-time"></i> {{ props.row.testTime }}</span>
                                        </el-form-item>
                                    </el-col>
                                </el-row>
                                <el-row :gutter="20">
                                    <el-col :span="24">
                                        <el-form-item label="请求参数">
                                            <pre class="code-block">{{ props.row.parameter }}</pre>
                                        </el-form-item>
                                    </el-col>
                                </el-row>
                                <el-row :gutter="20">
                                    <el-col :span="24">
                                        <el-form-item label="返回结果">
                                            <pre class="code-block json-block" v-highlightA><code>{{ props.row.responseData }}</code></pre>
                                        </el-form-item>
                                    </el-col>
                                </el-row>
                            </el-form>
                        </div>
                    </template>
                </el-table-column>
                <el-table-column type="index" label="#" width="60" align="center">
                </el-table-column>
                <el-table-column prop="name" label="接口名称" min-width="25%" sortable show-overflow-tooltip>
                </el-table-column>
                <el-table-column prop="automationTestCase" label="用例名称" min-width="25%" sortable show-overflow-tooltip>
                </el-table-column>
                <el-table-column prop="apiAddress" label="请求地址" min-width="20%" sortable show-overflow-tooltip>
                </el-table-column>
                <el-table-column prop="examineType" label="校验方式" min-width="12%" sortable align="center">
                    <template slot-scope="scope">
                        <el-tag :type="getExamineTypeTag(scope.row.examineType)" size="small">{{ getExamineTypeText(scope.row.examineType) }}</el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="result" label="结果" min-width="10%" :filters="resultFilter" :filter-method="filterHandler" align="center">
                    <template slot-scope="scope">
                        <el-tag :type="getResultTag(scope.row.result)" size="small" effect="plain">{{ scope.row.result || 'NotRun' }}</el-tag>
                    </template>
                </el-table-column>
            </el-table>
        </div>
    </section>
</template>

<script>
    import { test } from '../../../api/api'
    import $ from 'jquery'
    import * as echarts from 'echarts'

    export default {
        name: "test-report",
        data(){
            return {
                pass: "",
                fail: "",
                not_run: "",
                error: "",
                total: "",
                listLoading: false,
                resultFilter: [
                    {text: 'ERROR', value: 'ERROR'},
                    {text: 'FAIL', value: 'FAIL'},
                    {text: 'NotRun', value: 'NotRun'},
                    {text: 'PASS', value: 'PASS'},
                ],
                tableData: [],
                pieChart: null,
                barChart: null
            }
        },
        methods: {
            back(){
                this.$router.go(-1);
            },
            getRequestTypeTag(type) {
                const typeMap = {
                    'GET': 'success',
                    'POST': 'primary',
                    'PUT': 'warning',
                    'DELETE': 'danger',
                    'PATCH': 'info'
                };
                return typeMap[type] || '';
            },
            getExamineTypeTag(type) {
                const typeMap = {
                    'no_check': 'info',
                    'only_check_status': 'success',
                    'json': 'warning',
                    'entirely_check': 'primary',
                    'Regular_check': 'danger'
                };
                return typeMap[type] || '';
            },
            getExamineTypeText(type) {
                const textMap = {
                    'no_check': '不校验',
                    'only_check_status': '校验 http 状态',
                    'json': 'JSON 校验',
                    'entirely_check': '完全校验',
                    'Regular_check': '正则校验'
                };
                return textMap[type] || type;
            },
            getResultTag(result) {
                const tagMap = {
                    'PASS': 'success',
                    'FAIL': 'danger',
                    'ERROR': 'danger',
                    'TimeOut': 'warning',
                    'NotRun': 'info'
                };
                return tagMap[result] || '';
            },
            initPieChart() {
                if (!this.pieChart) {
                    this.pieChart = echarts.init(this.$refs.pieChart);
                }

                const option = {
                    tooltip: {
                        trigger: 'item',
                        formatter: '{b}: {c} ({d}%)',
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        borderColor: '#409eff',
                        borderWidth: 1,
                        textStyle: { color: '#fff' }
                    },
                    legend: {
                        orient: 'vertical',
                        right: '10%',
                        top: 'center',
                        textStyle: { color: '#606266' },
                        itemGap: 15,
                        itemWidth: 12,
                        itemHeight: 12
                    },
                    color: ['#67c23a', '#f56c6c', '#e6a23c', '#909399'],
                    series: [
                        {
                            name: '测试结果',
                            type: 'pie',
                            radius: ['40%', '70%'],
                            center: ['40%', '50%'],
                            avoidLabelOverlap: false,
                            itemStyle: {
                                borderRadius: 10,
                                borderColor: '#fff',
                                borderWidth: 2,
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0,0,0,0.2)'
                            },
                            label: {
                                show: true,
                                position: 'outside',
                                formatter: '{b}\n{d}%',
                                color: '#303133',
                                fontSize: 12
                            },
                            emphasis: {
                                label: {
                                    show: true,
                                    fontSize: 14,
                                    fontWeight: 'bold'
                                },
                                itemStyle: {
                                    shadowBlur: 15,
                                    shadowOffsetX: 0,
                                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                                }
                            },
                            data: [
                                { value: this.pass || 0, name: '通过' },
                                { value: this.fail || 0, name: '失败' },
                                { value: this.error || 0, name: '错误' },
                                { value: this.not_run || 0, name: '未执行' }
                            ]
                        }
                    ]
                };

                this.pieChart.setOption(option);
            },
            initBarChart() {
                if (!this.barChart) {
                    this.barChart = echarts.init(this.$refs.barChart);
                }

                const option = {
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: { type: 'shadow' },
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        borderColor: '#409eff',
                        borderWidth: 1,
                        textStyle: { color: '#fff' }
                    },
                    grid: {
                        left: '3%',
                        right: '4%',
                        bottom: '3%',
                        top: '10%',
                        containLabel: true
                    },
                    xAxis: {
                        type: 'category',
                        data: ['通过', '失败', '错误', '未执行'],
                        axisTick: { alignWithLabel: true },
                        axisLabel: { color: '#606266' },
                        axisLine: { lineStyle: { color: '#dcdfe6' } }
                    },
                    yAxis: {
                        type: 'value',
                        minInterval: 1,
                        axisLabel: { color: '#606266' },
                        splitLine: { lineStyle: { color: '#ebeef5', type: 'dashed' } }
                    },
                    series: [
                        {
                            name: '数量',
                            type: 'bar',
                            barWidth: '50%',
                            itemStyle: {
                                borderRadius: [6, 6, 0, 0],
                                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                    { offset: 0, color: '#67c23a' },
                                    { offset: 1, color: '#95d475' }
                                ])
                            },
                            emphasis: {
                                itemStyle: {
                                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                        { offset: 0, color: '#85ce61' },
                                        { offset: 1, color: '#b3e19d' }
                                    ])
                                }
                            },
                            data: [
                                this.pass || 0,
                                this.fail || 0,
                                this.error || 0,
                                this.not_run || 0
                            ]
                        }
                    ]
                };

                this.barChart.setOption(option);
            },
            resizeCharts() {
                if (this.pieChart) this.pieChart.resize();
                if (this.barChart) this.barChart.resize();
            },
            tableRowStyle(row) {
                if (row.result === 'ERROR' || row.result === 'FAIL') {
                    return { background: '#fef0f0', transition: 'background 0.3s' };
                } else if (row.result === 'TimeOut') {
                    return { background: '#fdf6ec', transition: 'background 0.3s' };
                }
                return {};
            },
            filterHandler(value, row, column) {
                return row.result === value;
            },
            getTestResult() {
                this.listLoading = true;
                let self = this;
                $.ajax({
                    type: "get",
                    url: test + "/api/automation/test_report",
                    async: true,
                    data: { project_id: this.$route.params.project_id},
                    headers: {
                        Authorization: 'Token '+JSON.parse(localStorage.getItem('token'))
                    },
                    timeout: 5000,
                    success: function(data) {
                        self.listLoading = false;
                        if (data.code === '999999') {
                            self.total = data.data.total;
                            self.pass = data.data.pass;
                            self.fail = data.data.fail;
                            self.not_run = data.data.NotRun;
                            self.error = data.data.error;
                            self.tableData = data.data.data
                            self.tableData.forEach((i) =>{
                                i["responseData"] = JSON.parse(i["responseData"].replace(/'/g, "\"").replace(/None/g, "null").replace(/True/g, "true").replace(/False/g, "false"));
                            })
                            self.$nextTick(() => {
                                self.initPieChart();
                                self.initBarChart();
                            });
                        } else {
                            self.$message.error({
                                message: data.msg,
                                center: true,
                            })
                        }
                    },
                })
            },
        },
        mounted() {
            this.getTestResult();
            window.addEventListener('resize', this.resizeCharts);
        },
        beforeDestroy() {
            if (this.pieChart) this.pieChart.dispose();
            if (this.barChart) this.barChart.dispose();
            window.removeEventListener('resize', this.resizeCharts);
        }
    }
</script>

<style scoped>
/* 全局背景 */
.test-report-container {
    padding: 24px;
    background: #f0f2f6;
    min-height: calc(100vh - 84px);
}

/* 头部区域 */
.report-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding: 20px 24px;
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02), 0 1px 2px rgba(0, 0, 0, 0.03);
    transition: all 0.3s;
}

.return-list {
    border-radius: 12px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.3s;
    background: #f5f7fa;
    border: none;
    color: #409eff;
}

.return-list:hover {
    background: #ecf5ff;
    transform: translateX(-4px);
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.stats-cards {
    display: flex;
    gap: 16px;
}

.stat-card {
    padding: 16px 28px;
    border-radius: 20px;
    text-align: center;
    min-width: 120px;
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fc 100%);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    transition: all 0.3s cubic-bezier(0.2, 0, 0, 1);
    backdrop-filter: blur(2px);
    border: 1px solid rgba(255, 255, 255, 0.5);
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 20px rgba(0, 0, 0, 0.1);
}

.stat-pass {
    background: linear-gradient(135deg, #67c23a 0%, #5caf2a 100%);
    color: #fff;
    border: none;
}

.stat-fail {
    background: linear-gradient(135deg, #f56c6c 0%, #e54646 100%);
    color: #fff;
    border: none;
}

.stat-error {
    background: linear-gradient(135deg, #e6a23c 0%, #d48c1a 100%);
    color: #fff;
    border: none;
}

.stat-total {
    background: linear-gradient(135deg, #409eff 0%, #2c6e9e 100%);
    color: #fff;
    border: none;
}

.stat-value {
    font-size: 38px;
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 6px;
    letter-spacing: -0.5px;
}

.stat-label {
    font-size: 13px;
    opacity: 0.9;
    letter-spacing: 1px;
    font-weight: 500;
}

/* 图表区域 */
.chart-row {
    margin-bottom: 24px;
}

.chart-card {
    background: #fff;
    border-radius: 20px;
    padding: 20px 20px 12px 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02), 0 1px 2px rgba(0, 0, 0, 0.03);
    transition: all 0.3s;
    height: 360px;
    display: flex;
    flex-direction: column;
}

.chart-card:hover {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    transform: translateY(-2px);
}

.chart-title {
    font-size: 16px;
    font-weight: 600;
    color: #1f2f3d;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 2px solid #409eff;
    display: flex;
    align-items: center;
    gap: 8px;
}

.chart-title i {
    font-size: 18px;
    color: #409eff;
}

.echarts-chart {
    flex: 1;
    width: 100%;
    min-height: 260px;
}

/* 表格容器 */
.table-container {
    background: #fff;
    border-radius: 20px;
    padding: 0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02), 0 1px 2px rgba(0, 0, 0, 0.03);
    overflow: hidden;
}

.test-result-table {
    width: 100%;
    border-radius: 20px;
}

::v-deep .table-header-class th {
    background-color: #f7f9fc !important;
    color: #1f2f3d;
    font-weight: 600;
    font-size: 14px;
    border-bottom: 2px solid #e9ecef;
}

::v-deep .el-table__row {
    transition: all 0.2s;
}

::v-deep .el-table__row:hover > td {
    background-color: #f9fafc !important;
}

::v-deep .el-table--border, ::v-deep .el-table--group {
    border-color: #e9ecef;
}

::v-deep .el-table td, ::v-deep .el-table th.is-leaf {
    border-bottom: 1px solid #eef2f6;
}

/* 展开区域 */
.expand-content {
    padding: 24px 32px;
    background: #f9fafc;
    border-top: 1px solid #eef2f6;
    border-bottom: 1px solid #eef2f6;
}

.demo-table-expand {
    width: 100%;
}

.demo-table-expand .el-form-item {
    margin-bottom: 20px;
}

.demo-table-expand .el-form-item__label {
    font-weight: 600;
    color: #4a5a6e;
    width: 110px !important;
    font-size: 13px;
}

.form-value {
    color: #1f2f3d;
    font-size: 14px;
    line-height: 1.6;
}

.api-url {
    word-break: break-all;
    color: #409eff;
    font-family: monospace;
}

.code-block {
    background: #1e1f22;
    color: #d4d4d4;
    padding: 16px;
    border-radius: 12px;
    font-family: 'Fira Code', 'Consolas', monospace;
    font-size: 13px;
    line-height: 1.5;
    overflow-x: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
    max-height: 400px;
    margin: 0;
    border: 1px solid #2c2e31;
}

.json-block {
    background: #0d1117;
    border: 1px solid #30363d;
}

/* 表格内标签微调 */
::v-deep .el-tag {
    border-radius: 12px;
    padding: 0 10px;
    height: 26px;
    line-height: 24px;
    font-weight: 500;
}

::v-deep .el-tag--plain {
    background: transparent;
}

/* 响应式 */
@media (max-width: 768px) {
    .test-report-container {
        padding: 16px;
    }
    .report-header {
        flex-direction: column;
        align-items: stretch;
        gap: 16px;
    }
    .stats-cards {
        flex-wrap: wrap;
        justify-content: center;
    }
    .stat-card {
        flex: 1;
        min-width: 80px;
        padding: 12px 16px;
    }
    .stat-value {
        font-size: 28px;
    }
    .chart-card {
        height: auto;
        margin-bottom: 20px;
    }
    .expand-content {
        padding: 16px;
    }
}
</style>
<template>
  <el-container class="control-shell">
    <el-header class="header">
      <b>直播场控台</b>
      <el-tag type="success">{{ session.state }}</el-tag>
    </el-header>
    <el-main>
      <el-row :gutter="12">
        <el-col :span="7">
          <el-card shadow="never">
            <template #header>直播状态</template>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="平台">{{ session.platform }}</el-descriptions-item>
              <el-descriptions-item label="当前商品">{{ session.product }}</el-descriptions-item>
              <el-descriptions-item label="推流状态">{{ session.streamHealth }}</el-descriptions-item>
            </el-descriptions>
            <div class="actions">
              <el-button type="warning">人工接管</el-button>
              <el-button>打断播报</el-button>
              <el-button>切备用视频</el-button>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card shadow="never">
            <template #header>评论队列</template>
            <el-input v-model="mockComment" placeholder="模拟评论：这款多少钱">
              <template #append>
                <el-button @click="flow.submitMockComment(mockComment)">发送</el-button>
              </template>
            </el-input>
            <el-table :data="comments" class="section">
              <el-table-column prop="user" label="用户" width="90" />
              <el-table-column prop="content" label="评论" />
              <el-table-column prop="intent" label="意图" width="100" />
            </el-table>
          </el-card>
        </el-col>

        <el-col :span="9">
          <el-card shadow="never">
            <template #header>候选回答 / 审核</template>
            <el-alert title="所有 AI 播报必须先经过合规和人工审核" type="info" show-icon />
            <el-input v-model="candidate.answer" type="textarea" :rows="4" class="section" />
            <div class="risk-row">
              <span>合规风险：</span>
              <el-tag :type="riskTagType">{{ candidate.risk }}</el-tag>
            </div>
            <el-space wrap>
              <el-button type="primary" @click="flow.approvePendingReview">审核通过</el-button>
              <el-button type="danger">拒绝</el-button>
              <el-button>编辑后通过</el-button>
            </el-space>
            <h3>播报历史</h3>
            <el-timeline>
              <el-timeline-item
                v-for="item in speechHistory"
                :key="item.id"
                :type="item.status === 'finished' ? 'success' : 'warning'"
              >
                {{ item.text }} - {{ item.status }}
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useMockFlowStore } from './stores/mockFlow';

const flow = useMockFlowStore();
const mockComment = ref('这款多少钱？');
const session = reactive({
  platform: 'MockPlatform',
  product: '保湿面霜',
  state: 'LIVE',
  streamHealth: 'SRS preview ready',
});
const comments = [
  { user: '观众A', content: '这款多少钱？', intent: 'price' },
  { user: '观众B', content: '敏感肌可以用吗？', intent: 'suitability' },
];
const candidate = reactive({
  answer: '这款保湿面霜当前价格以页面为准，参考 SKU 价格为 129.00 元。',
  risk: 'low',
});
const speechHistory = [
  { id: 'speech-1', text: '欢迎来到直播间', status: 'finished' },
  { id: 'speech-2', text: '这款保湿面霜当前价格以页面为准', status: 'finished' },
];
const riskTagType = computed(() => (candidate.risk === 'low' ? 'success' : 'warning'));

onMounted(() => {
  void flow.loadProducts();
});
</script>

<style scoped>
.control-shell {
  min-height: 100vh;
}

.header {
  align-items: center;
  display: flex;
  gap: 12px;
}

.actions,
.section,
.risk-row {
  margin-top: 12px;
}

.risk-row {
  align-items: center;
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
</style>

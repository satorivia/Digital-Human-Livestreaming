import { defineStore } from 'pinia';
import { getData, postData } from '../api/client';

interface Product {
  id: string;
  title: string;
}

interface LiveSession {
  id: string;
  product_id: string;
  state: string;
}

interface CommentTask {
  id: string;
  content: string;
  intent: string;
}

interface ReviewTask {
  id: string;
  candidate_id: string;
  status: string;
}

interface SpeechTask {
  id: string;
  text: string;
  status: string;
}

interface MockCommentResult {
  comment_task: CommentTask;
  review: ReviewTask;
}

export const useMockFlowStore = defineStore('mockFlow', {
  state: () => ({
    products: [] as Product[],
    currentProduct: null as Product | null,
    currentSession: null as LiveSession | null,
    comments: [] as CommentTask[],
    pendingReview: null as ReviewTask | null,
    speeches: [] as SpeechTask[],
    loading: false,
    errorMessage: '',
  }),
  getters: {
    canSubmitComment: (state) => Boolean(state.currentSession && !state.loading),
    canApproveReview: (state) => Boolean(state.pendingReview && !state.loading),
  },
  actions: {
    async runAction(action: () => Promise<void>) {
      this.loading = true;
      this.errorMessage = '';
      try {
        await action();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '未知错误';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async loadProducts() {
      await this.runAction(async () => {
        this.products = await getData<Product[]>('/products');
        this.currentProduct = this.products[0] ?? null;
      });
    },
    async createMockSession(productId: string) {
      await this.runAction(async () => {
        const session = await postData<LiveSession>('/live-sessions', { product_id: productId });
        this.currentSession = session;
        await postData(`/live-sessions/${session.id}/start`);
      });
    },
    async submitMockComment(content: string) {
      await this.runAction(async () => {
        if (!this.currentSession) {
          throw new Error('live session is required before submitting comments');
        }
        const result = await postData<MockCommentResult>(
          `/live-sessions/${this.currentSession.id}/mock-comments`,
          { content },
        );
        this.comments.push(result.comment_task);
        this.pendingReview = result.review;
      });
    },
    async approvePendingReview() {
      await this.runAction(async () => {
        if (!this.pendingReview) {
          throw new Error('pending review is required before approval');
        }
        const result = await postData<{
          speech_task: SpeechTask;
        }>(`/review-tasks/${this.pendingReview.id}/approve`, { reviewer_id: 'operator' });
        this.speeches.push(result.speech_task);
        this.pendingReview = null;
      });
    },
    async refreshSpeechTasks() {
      await this.runAction(async () => {
        this.speeches = await getData<SpeechTask[]>('/speech-tasks');
      });
    },
  },
});

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

export const useMockFlowStore = defineStore('mockFlow', {
  state: () => ({
    products: [] as Product[],
    currentProduct: null as Product | null,
    currentSession: null as LiveSession | null,
    comments: [] as CommentTask[],
    pendingReview: null as ReviewTask | null,
    speeches: [] as SpeechTask[],
  }),
  actions: {
    async loadProducts() {
      this.products = await getData<Product[]>('/products');
      this.currentProduct = this.products[0] ?? null;
    },
    async createMockSession(productId: string) {
      const session = await postData<LiveSession>('/live-sessions', { product_id: productId });
      this.currentSession = session;
      await postData(`/live-sessions/${session.id}/start`);
    },
    async submitMockComment(content: string) {
      if (!this.currentSession) {
        throw new Error('live session is required before submitting comments');
      }
      const result = await postData<{
        comment_task: CommentTask;
        review: ReviewTask;
      }>(`/live-sessions/${this.currentSession.id}/mock-comments`, { content });
      this.comments.push(result.comment_task);
      this.pendingReview = result.review;
    },
    async approvePendingReview() {
      if (!this.pendingReview) {
        throw new Error('pending review is required before approval');
      }
      const result = await postData<{
        speech_task: SpeechTask;
      }>(`/review-tasks/${this.pendingReview.id}/approve`, { reviewer_id: 'operator' });
      this.speeches.push(result.speech_task);
    },
    async refreshSpeechTasks() {
      this.speeches = await getData<SpeechTask[]>('/speech-tasks');
    },
  },
});

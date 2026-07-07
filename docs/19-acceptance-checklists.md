# 19. 验收清单

## 1. 阶段 0 验收

- [ ] 仓库结构符合 docs/03-repo-structure.md。
- [ ] `AGENTS.md` 存在。
- [ ] `.env.example` 存在且不包含真实密钥。
- [ ] `make up` 可启动 Postgres/Redis/Qdrant/MinIO/SRS。
- [ ] `make migrate` 可执行。
- [ ] `/api/v1/healthz` 返回正常。
- [ ] admin-web 可启动。
- [ ] control-web 可启动。
- [ ] `make test` 可运行。

## 2. 阶段 1 验收

- [ ] 可创建商家。
- [ ] 可创建商品。
- [ ] 可创建 SKU。
- [ ] 可创建价格。
- [ ] 可创建 FAQ。
- [ ] 可创建商品卖点。
- [ ] 可执行商品知识库索引。
- [ ] MockPlatformAdapter 可模拟评论。
- [ ] CommentRouter 可创建 comment_task。
- [ ] LLMGateway Mock 可生成候选回答。
- [ ] ComplianceService 可输出风险等级。
- [ ] HumanReviewService 可审核通过/拒绝/改写。
- [ ] TTSService Mock 可生成假音频。
- [ ] AvatarGateway Mock 可完成播报。
- [ ] 场控台可完成评论到播报链路。
- [ ] E2E 测试通过。

## 3. 阶段 2 验收

- [ ] 音色管理可用。
- [ ] 音色授权校验可用。
- [ ] TTS 真实 Provider 至少一个可用。
- [ ] AvatarGateway 能调用 LiveTalkingProvider。
- [ ] 可完成真实数字人播报。
- [ ] 可打断当前播报。
- [ ] 可切换待机 / fallback。
- [ ] SRS 可返回预览地址。
- [ ] OBS 可采集画面或 RTMP。

## 4. 淘宝 Adapter 验收

- [ ] 平台账号配置可保存。
- [ ] 淘宝 raw event 可入库。
- [ ] 淘宝评论可转 PlatformEvent。
- [ ] 淘宝上下播可转 PlatformEvent。
- [ ] 淘宝订单可转 PlatformEvent。
- [ ] 商品 ID 映射可用。
- [ ] 淘宝评论可进入问答链路。
- [ ] 淘宝订单可记录。

## 5. 抖音 Adapter 验收

- [ ] 平台账号配置可保存。
- [ ] 互动数据任务启动/停止/查询状态封装完成。
- [ ] 抖音评论可转 PlatformEvent。
- [ ] 平台警告可进入系统告警。
- [ ] 中高风险默认人审。
- [ ] 平台警告触发暂停自动互动。

## 6. 合规验收

- [ ] 每条 AI 播报有 compliance_result。
- [ ] blocked 不会创建 speech_task。
- [ ] high 不会自动播报。
- [ ] medium 默认进入人审。
- [ ] 价格回答经过价格一致性校验。
- [ ] AI 标识配置可用。
- [ ] 直播间角标配置可用。
- [ ] 定时 AI 身份提示可用。
- [ ] 所有审核操作写 audit_log。

## 7. 业务验收

- [ ] 数字人可连续讲解商品。
- [ ] 观众提问可进入场控台。
- [ ] AI 能生成候选回答。
- [ ] 人工可编辑后播报。
- [ ] 价格不胡编。
- [ ] 卖点不胡编。
- [ ] 敏感问题能拦截。
- [ ] 人工接管可用。
- [ ] 下播后可导出日志。

## 8. 安全验收

- [ ] 仓库无密钥。
- [ ] 日志脱敏。
- [ ] 平台 token 不明文输出。
- [ ] 音色有授权记录。
- [ ] 数字人形象有授权记录。
- [ ] 文件上传限制类型和大小。
- [ ] 权限控制可用。

## 9. 上线前人工检查

- [ ] 平台规则已由运营/法务确认。
- [ ] 直播间 AI 标识已配置。
- [ ] 商品话术已审核。
- [ ] 音色授权已确认。
- [ ] 数字人形象授权已确认。
- [ ] 人工接管人员在岗。
- [ ] 平台账号状态正常。
- [ ] OBS/SRS 推流测试通过。
- [ ] 应急预案确认。

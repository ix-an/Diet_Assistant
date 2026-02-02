<template>
	<view class="login-container">
		<!-- 新增欢迎卡片 -->
		<view class="welcome-card">
			<text class="welcome-title">🍋 欢迎来到柠檬饮食助手 (*^▽^*)</text>
			<text class="welcome-desc">请登录，如果无账号会自动注册</text>
		</view>

		<!-- 登录/自动注册表单区域 -->
		<uni-section title="用户登录" type="line">
			<view class="example">
				<uni-forms ref="baseForm" :modelValue="baseFormData">
					<!-- 用户名输入项 -->
					<uni-forms-item label="用户名" required>
						<uni-easyinput v-model="baseFormData.username" placeholder="请输入用户名" />
					</uni-forms-item>
					<!-- 密码输入项 -->
					<uni-forms-item label="密码" required>
						<uni-easyinput type="password" v-model="baseFormData.password" placeholder="请输入密码" />
					</uni-forms-item>

					<!-- 登录按钮（点击后触发登录/自动注册逻辑） -->
					<button type="primary" @tap="handleLoginOrRegister">登录</button>
				</uni-forms>
			</view>
		</uni-section>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				// 表单数据：统一为username（用户名）、password（密码）
				baseFormData: {
					username: '',
					password: ''
				}
			}
		},
		methods: {
			/**
			 * 核心逻辑：登录 + 自动注册一体化处理
			 * 流程：1. 表单验证 → 2. 调用登录接口 → 3. 根据接口返回做处理：
			 *    - 用户名密码正确 → 登录成功
			 *    - 用户名存在但密码错误 → 提示密码错误
			 *    - 用户名不存在 → 自动调用注册接口
			 */
			handleLoginOrRegister() {
				// 1. 表单非空验证
				const { username, password } = this.baseFormData;

				// 验证用户名非空
				if (username === '') {
					uni.showToast({
						title: '用户名必填',
						icon: 'error',
						duration: 2000
					});
					return false;
				}

				// 验证密码非空
				if (!password) {
					uni.showToast({
						title: '请输入密码',
						icon: 'none',
						duration: 2000
					});
					return;
				}

				// 2. 调用登录接口
				this.userLogin(username, password);
			},

			/**
			 * 登录请求方法
			 * @param {String} username 用户名
			 * @param {String} password 密码
			 */
			userLogin(username, password) {
				uni.request({
					url: 'http://localhost:8000/user/login/', // 登录接口地址
					method: 'POST',
					data: {
						username: username, // 传递用户名
						password: password  // 传递密码
					},
					header: {
						'content-type': 'application/x-www-form-urlencoded'
					},
					success: (res) => {
						console.log('完整返回:', JSON.stringify(res.data));
						const { status, message } = res.data;

						// 场景1：登录成功（用户名密码都正确）
						if (res.data.status === 'success') {
						  uni.showToast({
						    title: '登录成功~',
						    icon: 'success'
						  });
							
						  // 缓存数据到本地
						  uni.setStorageSync('currentUser', {
						      user_id: res.data.data.id,
						      username: res.data.data.username,
						      avatarUrl: res.data.data.avatar
						    });
						  console.log("缓存成功")
							
						  // switchTab + 短暂延迟，适配TabBar页面
						  setTimeout(() => {
						    uni.switchTab({
						      url: "/pages/index/index"
						    });
						  }, 500);
						}
						// 场景2：密码错误（用户名存在但密码不对）
						else if (message.includes('密码错误') || (status === 'fail' && !message.includes('不存在'))) {
							uni.showToast({
								title: '密码错误',
								icon: 'error',
								duration: 2000
							});
						} 
						// 场景3：用户名不存在 → 自动注册
						else if (message.includes('用户不存在') || (status === 'fail' && message.includes('不存在'))) {
							uni.showToast({
								title: '用户不存在，自动注册中...',
								icon: 'none',
								duration: 1500
							});
							// 调用注册接口
							this.userRegister(username, password);
						} 
						// 其他异常提示
						else {
							uni.showToast({
								title: message || '登录失败',
								icon: 'error',
								duration: 2000
							});
						}
					},
					fail: (err) => {
						// 网络异常提示
						uni.showToast({
							title: '网络异常，登录失败',
							icon: 'error'
						});
						console.error('登录请求失败：', err);
					}
				});
			},

			/**
			 * 自动注册请求方法（登录失败且用户不存在时调用）
			 * @param {String} username 用户名
			 * @param {String} password 密码
			 */
			userRegister(username, password) {
				uni.request({
					url: 'http://localhost:8000/user/reg/', // 注册接口地址
					method: 'POST',
					data: {
						username: username,
						password: password,
					},
					header: {
						'content-type': 'application/x-www-form-urlencoded'
					},
					success: (res) => {
						console.log('注册接口返回：', res.data);
						const { status, message } = res.data;

						// 注册成功 → 再次调用登录接口（完成自动登录）
						if (status === 'success') {
							uni.showToast({
								title: '注册成功，自动登录中...',
								icon: 'success',
								duration: 1500
							});
							// 延迟1.5秒登录，提升用户体验
							setTimeout(() => {
								this.userLogin(username, password);
							}, 1500);
						} 
						// 注册失败（如用户名已存在，理论上不会触发，仅兜底）
						else {
							uni.showToast({
								title: message || '注册失败',
								icon: 'error',
								duration: 2000
							});
						}
					},
					fail: (err) => {
						uni.showToast({
							title: '网络异常，注册失败',
							icon: 'error'
						});
						console.error('注册请求失败：', err);
					}
				});
			}
		}
	}
</script>

<style scoped>
	/* 定义奶油风CSS变量 */
	page {
		--cream-bg: #fdfbf8;          /* 主背景色 */
		--cream-primary: #e8dcca;     /* 主要色调（按钮、发送按钮背景） */
		--cream-secondary: #d4e6f1;   /* 次要色调（用户消息背景） */
		--cream-text-main: #5c544b;   /* 主要文字颜色 */
		--cream-text-secondary: #a89f94; /* 次要文字颜色（占位符） */
		--cream-shadow: 0 4rpx 16rpx rgba(200, 190, 170, 0.15); /* 通用阴影 */
		--cream-radius: 16rpx;        /* 通用圆角 */
		--cream-radius-sm: 8rpx;      /* 小圆角 */
	}

	/* 页面容器整体样式 */
	.login-container {
		padding: 20rpx;
		background-color: var(--cream-bg);
		min-height: 100vh;
		box-sizing: border-box;
	}

	/* 欢迎卡片样式 */
	.welcome-card {
		background-color: #fff;
		border-radius: var(--cream-radius);
		padding: 30rpx 20rpx;
		margin-bottom: 30rpx;
		text-align: center;
		box-shadow: var(--cream-shadow);
	}

	/* 欢迎标题样式 */
	.welcome-title {
		font-size: 32rpx;
		font-weight: 600;
		color: var(--cream-text-main);
		display: block; /* 独占一行 */
		margin-bottom: 12rpx;
		letter-spacing: 1rpx;
	}

	/* 欢迎描述小字样式 */
	.welcome-desc {
		font-size: 26rpx;
		color: var(--cream-text-secondary);
		display: block;
		line-height: 1.4;
	}

	/* 表单区域样式 */
	.example {
		padding: 30rpx 25rpx;
		background-color: #fff;
		border-radius: var(--cream-radius);
		box-shadow: var(--cream-shadow);
	}

	/* 表单项样式优化 */
	.uni-forms-item {
		margin-bottom: 25rpx;
	}
	.uni-forms-item .uni-forms-item__label {
		font-size: 28rpx;
		color: var(--cream-text-main);
		font-weight: 500;
	}
	/* 输入框样式 */
	.uni-easyinput {
		--placeholder-color: var(--cream-text-secondary);
		--input-color: var(--cream-text-main);
		--input-border-color: var(--cream-primary);
		border-radius: var(--cream-radius-sm);
		background-color: var(--cream-bg);
	}
	.uni-easyinput__input {
		font-size: 28rpx;
		padding: 16rpx 12rpx;
	}

	/* 登录按钮样式 */
	button {
		margin-top: 30rpx;
		height: 88rpx;
		line-height: 88rpx;
		border-radius: var(--cream-radius);
		background-color: var(--cream-primary) !important;
		color: var(--cream-text-main) !important;
		font-size: 30rpx;
		font-weight: 500;
		box-shadow: var(--cream-shadow);
		border: none !important;
		letter-spacing: 2rpx;
	}
	button::after {
		border: none !important;
	}
	button:active {
		background-color: #e0d0bc !important;
		transform: scale(0.98);
		transition: all 0.2s ease;
	}

	/* 适配uni-section组件样式 */
	.uni-section {
		--uni-section-title-color: var(--cream-text-main);
		--uni-section-line-color: var(--cream-primary);
		margin-bottom: 0;
	}
	.uni-section__title {
		font-size: 28rpx;
		font-weight: 600;
	}
</style>
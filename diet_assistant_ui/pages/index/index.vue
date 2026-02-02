<template>
  <!-- ================= 轮播图区域 ================= -->
  <!-- 使用 v-for 管理轮播图，避免结构写死，便于维护 -->
  <swiper
    class="myswiper"
    :indicator-dots="true"
    :autoplay="true"
    :interval="4000"
    :duration="600"
    circular
  >
    <swiper-item v-for="(item, index) in swiperList" :key="index">
      <view class="swiper-item">
        <!-- aspectFill 保证图片铺满但不变形 -->
        <image :src="item" mode="aspectFill"></image>
      </view>
    </swiper-item>
  </swiper>

  <view class="page">
    <!-- ================= 顶部 banner（进入 AI 助手入口） ================= -->
    <view class="banner" @click="goAssistant">
      <image class="banner-icon" src="/static/avatar.png" mode="aspectFit" />
      <view class="banner-text">
        <view class="banner-title">今天要和柠柠聊点什么？</view>
        <view class="banner-sub">
          你变好的每一步都有我陪伴 <br />
          智能食谱 | 健身知识 | 热量计算
        </view>
      </view>
    </view>

    <!-- ================= 功能入口 ================= -->
    <view class="grid">
      <!-- 第一行 -->
      <view class="grid-item">
        <image class="grid-icon" src="/static/橘猫.png" />
        <text class="grid-text">断食</text>
      </view>
      <view class="grid-item">
        <image class="grid-icon" src="/static/可达鸭.png" />
        <text class="grid-text">喝水</text>
      </view>
      <view class="grid-item">
        <image class="grid-icon" src="/static/柯基.png" />
        <text class="grid-text">运动</text>
      </view>
      <view class="grid-item">
        <image class="grid-icon" src="/static/荷兰猪.png" />
        <text class="grid-text">食谱</text>
      </view>

      <!-- 第二行 -->
	  <view class="grid-item">
	    <image class="grid-icon" src="/static/羊.png" />
	    <text class="grid-text">经期</text>
	  </view>
	  <view class="grid-item">
	    <image class="grid-icon" src="/static/三花猫.png" />
	    <text class="grid-text">数据</text>
	  </view>
      <view class="grid-item">
        <image class="grid-icon" src="/static/布偶猫.png" />
        <text class="grid-text">活动</text>
      </view>
      <view class="grid-item">
        <image class="grid-icon" src="/static/更多犬种.png" />
        <text class="grid-text">商城</text>
      </view>
    </view>

    <!-- ================= 底部卡片 ================= -->
    <view class="bottom">
      <view class="bottom-card">
        <image class="bottom-icon" src="/static/图标选中/大型植物.png" />
        <view>
          <view class="bottom-title">我的食谱</view>
          <view class="bottom-sub">智能定制食谱</view>
        </view>
      </view>

      <view class="bottom-card">
        <image class="bottom-icon" src="/static/图标选中/tupian选中.png" />
        <view>
          <view class="bottom-title">饮食记录</view>
          <view class="bottom-sub">一句话记录饮食</view>
        </view>
      </view>
    </view>
  </view>

</template>

<script>
export default {
  data() {
    return {
      /* 轮播图数据：仅维护数组即可 */
      swiperList: [
        '/static/轮播图/sofine.png',
        '/static/轮播图/onlytree.png',
        '/static/轮播图/柠檬共和国.png'
      ],

      /* uni-fab 配置（原逻辑保留） */
      horizontal: 'right',
      vertical: 'bottom',
      direction: 'vertical',
      pattern: {
        color: '#E8DCCA',
        backgroundColor: '#fff',
        selectedColor: '#E8DCCA',
        buttonColor: '#E8DCCA',
        iconColor: '#5c544b'
      },
      content: [
        {
          iconPath: '/static/图标/盆栽.png',
          selectedIconPath: '/static/图标选中/盆栽选中.png',
          text: 'AI助手',
          active: true
        },
        {
          iconPath: '/static/h.png',
          selectedIconPath: '/static/h1.png',
          text: '首页',
          active: false
        }
      ]
    }
  },

  /* 处理返回键关闭 fab */
  onBackPress() {
    if (this.$refs.fab.isShow) {
      this.$refs.fab.close()
      return true
    }
    return false
  },

  methods: {
    /* 顶部 banner 进入 AI 助手 */
    goAssistant() {
      uni.navigateTo({
        url: '/pages/assistant/assistant'
      })
    },

  }
}
</script>

<style>
/* ================= 奶油风基础变量 ================= */
page {
  --cream-bg: #fdfbf8;
  --cream-text-main: #5c544b;
  --cream-text-sub: #a89f94;
  --cream-shadow: 0 4rpx 16rpx rgba(200, 190, 170, 0.15);
}

/* ================= 轮播图 ================= */
.myswiper {
  width: 100%;
  height: 800rpx;
}

.myswiper image {
  width: 100%;
  height: 800rpx;
}

/* ================= 页面 ================= */
.page {
  padding: 24rpx;
  background-color: var(--cream-bg);
}

/* ================= banner ================= */
.banner {
  display: flex;
  align-items: center;
  background: #ffffff;
  border-radius: 24rpx;
  padding: 24rpx;
  margin-bottom: 32rpx;
  box-shadow: var(--cream-shadow);
}

.banner-icon {
  width: 96rpx;
  height: 96rpx;
  margin-right: 20rpx;
}

.banner-title {
  font-size: 32rpx;
  font-weight: bold;
  color: var(--cream-text-main);
  margin-bottom: 12rpx;
}

.banner-sub {
  font-size: 22rpx;
  color: var(--cream-text-sub);
  line-height: 32rpx;
}

.banner-arrow {
  width: 36rpx;
  height: 36rpx;
}

.banner-text {
  margin-left: 28rpx;   /* ⭐ 控制图标和文字之间的距离 */
}

/* ================= 功能入口 ================= */
.grid {
  display: flex;
  flex-wrap: wrap;
  background: #ffffff;
  border-radius: 24rpx;
  padding: 24rpx 0;
  margin-bottom: 32rpx;
  box-shadow: var(--cream-shadow);
}

.grid-item {
  width: 25%;
  margin-bottom: 32rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.grid-icon {
  width: 72rpx;
  height: 72rpx;
  margin-bottom: 12rpx;
}

.grid-text {
  font-size: 24rpx;
  color: var(--cream-text-main);
}

/* ================= 底部卡片 ================= */
.bottom {
  display: flex;
  justify-content: space-between;
}

.bottom-card {
  width: 290rpx;
  background: #ffffff;
  border-radius: 24rpx;
  padding: 24rpx;
  display: flex;
  align-items: center;
  box-shadow: var(--cream-shadow);
}

.bottom-icon {
  width: 72rpx;
  height: 72rpx;
  margin-right: 20rpx;
}

.bottom-title {
  font-size: 28rpx;
  font-weight: bold;
  color: var(--cream-text-main);
  margin-bottom: 8rpx;
}

.bottom-sub {
  font-size: 22rpx;
  color: var(--cream-text-sub);
}
</style>



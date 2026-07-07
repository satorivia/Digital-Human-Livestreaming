<template><el-container><el-header><b>Admin Web 商品管理</b></el-header><el-main><el-card><el-button type="primary">新建商品</el-button><el-table :data="products"><el-table-column prop="title" label="商品"/><el-table-column prop="status" label="索引状态"/></el-table></el-card></el-main></el-container></template>
<script setup lang="ts">const products=[{title:'保湿面霜',status:'mock indexed'}]</script>

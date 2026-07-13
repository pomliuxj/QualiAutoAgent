<template>
  <div class="about-page">
    <div class="doc-container">
      <iframe
        src="../../static/自动化平台.pdf"
        class="doc-iframe"
        frameborder="0"
        allowfullscreen
      ></iframe>
    </div>
  </div>
</template>

<script>
export default {
  name: 'About',
}
</script>

<style scoped lang="scss">
.about-page {
  // Fill the remaining space below breadcrumb.
  // Header: 56px, Breadcrumb: ~50px, page-content padding: 20+24=44px
  height: calc(100vh - 56px - 50px - 44px);
  min-height: 500px;
  display: flex;
  flex-direction: column;
}

.doc-container {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #E5E7EB;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.doc-iframe {
  width: 100%;
  height: 100%;
  border: none;
}
</style>

<template>
  <div 
    class="custom-node tooltip-wrapper" 
    :style="{ 
      backgroundColor: data.color || 'white',
      width: data.width ? `${data.width}px` : 'auto',
      height: data.height ? `${data.height}px` : 'auto',
      border: '1px solid #bbb'
    }"
  >
    <!-- Target handle (input) on left -->
    <Handle type="target" :position="Position.Left" />
    
    <!-- Node content -->
    <div class="node-header">{{ data.label }}</div>

    <!-- Tooltip content -->
    <div v-if="data.description.length > 0" class="tooltip-content">
      <span v-for="(item, index) in data.description" :key="index" class="tag">
        {{ item }}
      </span>
    </div>
    
    <!-- Source handle (output) on right -->
    <Handle type="source" :position="Position.Right" />
  </div>
</template>

<script setup>
import { Handle, Position } from '@vue-flow/core'

// Props from VueFlow
defineProps(['id', 'data', 'label'])
</script>

<style>
.custom-node {
  padding: 10px;
  position: relative;
  min-width: 0;
  min-height: 0;
}

.node-header {
  text-align: center;
  word-wrap: break-word;
}

.tooltip-wrapper {
  position: relative;
  font-family: Roboto;
  font-size: 12px;
}

.tooltip-content {
  visibility: hidden;
  opacity: 0;

  /* IMPORTANT: make it flex container by default */
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  gap: 8px;

  max-width: 400px;
  padding: 8px 12px;
}

/* no need for separate horizontal-tags flex rules anymore */
.tooltip-content.horizontal-tags {
  white-space: normal;
}

/* tags */
.tag {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 11px;
  white-space: nowrap;
}

/* hover */
.tooltip-wrapper:hover .tooltip-content {
  visibility: visible;
  opacity: 1;
}

/* Tooltip arrow */
.tooltip-content::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 5px;
  border-style: solid;
  border-color: #333 transparent transparent transparent;
}
</style>
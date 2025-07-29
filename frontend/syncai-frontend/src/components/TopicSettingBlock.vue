<template>
  <div class="topic-setting">
    <input
      :value="topic"
      @input="$emit('update:topic', $event.target.value)"
      placeholder="輸入目前討論主題…"
    />
    <input
      :value="timerInput"
      type="number"
      min="10"
      max="3600"
      style="width:80px;"
      @input="$emit('update:timerInput', Number($event.target.value))"
    /> 秒
    <button @click="onStart" :disabled="countdownActive">啟動倒數</button>
    <button @click="onReset" :disabled="!countdownActive">重設倒數</button>
    <label style="margin-left:1.5em;">
      <input
        type="checkbox"
        :checked="anonymousMode"
        @change="$emit('update:anonymousMode', $event.target.checked)"
      />
      匿名留言
    </label>
  </div>
</template>

<script setup>
const props = defineProps(['topic', 'timerInput', 'countdownActive', 'anonymousMode'])
const emit = defineEmits(['start', 'reset', 'update:topic', 'update:timerInput', 'update:anonymousMode'])

const onStart = () => emit('start')
const onReset = () => emit('reset')
</script>

<style scoped>
.topic-setting {
  display: flex;
  align-items: center;
  gap: 0.9em;
  margin-bottom: 1.4em;
}
.topic-setting input[type="text"] {
  flex: 1;
  padding: 0.4em 0.7em;
  border-radius: 7px;
  border: 1px solid #444;
  background: #2c2d33;
  color: #fff;
  font-size: 1em;
}
.topic-setting input[type="number"] {
  padding: 0.35em 0.3em;
  border-radius: 6px;
  border: 1px solid #444;
  background: #2c2d33;
  color: #fff;
  font-size: 1em;
}
.topic-setting button {
  padding: 0.45em 1.1em;
  border-radius: 7px;
  border: none;
  background: #007bff;
  color: #fff;
  font-weight: bold;
  cursor: pointer;
  font-size: 1em;
  margin-right: 2px;
}
.topic-setting button:disabled {
  background: #999;
  cursor: not-allowed;
}
</style>
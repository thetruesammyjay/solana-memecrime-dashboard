<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-gray-800 rounded-lg max-w-md w-full p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">
            <slot name="title" />
          </h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-white">
            &times;
          </button>
        </div>
        <div class="mb-4">
          <slot />
        </div>
        <div class="flex justify-end gap-2">
          <slot name="actions" />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

defineEmits(['close'])
</script>
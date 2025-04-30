<template>
  <button
    @click="connect"
    class="bg-solana-green hover:bg-solana-green/80 text-black px-4 py-2 rounded-lg text-sm font-medium transition-colors"
  >
    {{ buttonText }}
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useWalletStore } from '@/stores/wallet'

const wallet = useWalletStore()

const buttonText = computed(() => {
  return wallet.connected 
    ? `${wallet.publicKey?.slice(0, 4)}...${wallet.publicKey?.slice(-4)}`
    : 'Connect Wallet'
})

const connect = async () => {
  if (wallet.connected) {
    await wallet.disconnect()
  } else {
    await wallet.connect()
  }
}
</script>
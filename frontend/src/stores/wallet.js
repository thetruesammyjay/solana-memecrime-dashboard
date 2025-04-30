import { defineStore } from 'pinia'
import { ref } from 'vue'
import { Connection, clusterApiUrl } from '@solana/web3.js'

export const useWalletStore = defineStore('wallet', () => {
  const publicKey = ref(null)
  const connected = ref(false)
  const connection = new Connection(clusterApiUrl('mainnet-beta'))

  async function connect() {
    try {
      // Actual wallet connection logic would go here
      connected.value = true
      publicKey.value = 'FakePublicKeyForDemo'
    } catch (error) {
      console.error('Wallet connection error:', error)
    }
  }

  async function disconnect() {
    publicKey.value = null
    connected.value = false
  }

  return {
    publicKey,
    connected,
    connect,
    disconnect
  }
})
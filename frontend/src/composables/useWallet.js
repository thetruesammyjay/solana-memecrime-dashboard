import { computed } from 'vue'
import { useWalletStore } from '@/stores/wallet'
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base'
import { PhantomWalletAdapter } from '@solana/wallet-adapter-wallets'

export function useWallet() {
  const store = useWalletStore()
  
  const wallets = computed(() => [
    new PhantomWalletAdapter(),
    // Add other wallets as needed
  ])

  const connect = async () => {
    await store.connect()
  }

  const disconnect = async () => {
    await store.disconnect()
  }

  return {
    wallets,
    publicKey: computed(() => store.publicKey),
    connected: computed(() => store.connected),
    connect,
    disconnect
  }
}
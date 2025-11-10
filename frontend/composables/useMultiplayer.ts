/**
 * useMultiplayer composable
 * Handles Supabase Realtime subscriptions for multiplayer quests
 * Supports 2-8 player rooms with shared relic fusion
 */
import { useSupabaseClient } from '#imports'

export interface Player {
  id: string
  name: string
  position?: [number, number, number]
  selectedRelic?: string
}

export interface Room {
  id: string
  name: string
  players: Player[]
  maxPlayers: number
  questTheme: string
  relicFusions: any[]
}

export const useMultiplayer = (roomId?: string) => {
  const supabase = useSupabaseClient()
  const currentRoom = ref<Room | null>(null)
  const players = ref<Player[]>([])
  const isConnected = ref(false)
  const error = ref<string | null>(null)

  // Realtime channel
  let channel: any = null

  /**
   * Join or create a multiplayer room
   */
  const joinRoom = async (
    roomName: string,
    playerName: string,
    maxPlayers: number = 8
  ): Promise<string> => {
    try {
      // Get current user
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('Not authenticated')

      // Create or get room
      let room: Room
      
      if (roomId) {
        // Join existing room
        const { data, error: fetchError } = await supabase
          .from('quests')
          .select('*')
          .eq('id', roomId)
          .single()

        if (fetchError) throw fetchError
        room = data as any
      } else {
        // Create new room
        const { data: newRoom, error: createError } = await supabase
          .from('quests')
          .insert({
            theme: roomName,
            status: 'active'
          })
          .select()
          .single()

        if (createError) throw createError
        room = newRoom as any
      }

      // Add player to room
      const player: Player = {
        id: user.id,
        name: playerName
      }

      // Subscribe to realtime updates
      await subscribeToRoom(room.id)

      currentRoom.value = {
        id: room.id,
        name: room.theme,
        players: [...players.value, player],
        maxPlayers,
        questTheme: room.theme,
        relicFusions: room.relic_fusions || []
      }

      players.value = currentRoom.value.players
      isConnected.value = true

      return room.id
    } catch (err: any) {
      error.value = err.message
      throw err
    }
  }

  /**
   * Subscribe to room updates via Supabase Realtime
   */
  const subscribeToRoom = async (roomId: string) => {
    // Unsubscribe from previous channel if exists
    if (channel) {
      await supabase.removeChannel(channel)
    }

    // Create new channel
    channel = supabase
      .channel(`room:${roomId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'quests',
          filter: `id=eq.${roomId}`
        },
        (payload: any) => {
          handleRoomUpdate(payload)
        }
      )
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'sessions',
          filter: `student_id=in.(${players.value.map(p => p.id).join(',')})`
        },
        (payload: any) => {
          handlePlayerProgress(payload)
        }
      )
      .subscribe((status: string) => {
        if (status === 'SUBSCRIBED') {
          isConnected.value = true
        } else if (status === 'CHANNEL_ERROR') {
          error.value = 'Failed to connect to room'
          isConnected.value = false
        }
      })
  }

  /**
   * Handle room updates from Realtime
   */
  const handleRoomUpdate = (payload: any) => {
    if (payload.eventType === 'UPDATE' && payload.new) {
      const updatedRoom = payload.new
      currentRoom.value = {
        ...currentRoom.value!,
        relicFusions: updatedRoom.relic_fusions || []
      }
    }
  }

  /**
   * Handle player progress updates
   */
  const handlePlayerProgress = (payload: any) => {
    // Update player progress in UI
    // This would trigger UI updates for shared progress
    console.log('Player progress update:', payload)
  }

  /**
   * Share relic fusion with other players
   */
  const shareRelicFusion = async (relic1: string, relic2: string, result: any) => {
    if (!currentRoom.value) return

    try {
      const fusion = {
        relics: [relic1, relic2],
        result,
        timestamp: new Date().toISOString()
      }

      const updatedFusions = [...currentRoom.value.relicFusions, fusion]

      const { error: updateError } = await supabase
        .from('quests')
        .update({ relic_fusions: updatedFusions })
        .eq('id', currentRoom.value.id)

      if (updateError) throw updateError

      currentRoom.value.relicFusions = updatedFusions
    } catch (err: any) {
      error.value = err.message
    }
  }

  /**
   * Update player position (for 3D realm)
   */
  const updatePlayerPosition = async (position: [number, number, number]) => {
    if (!currentRoom.value) return

    // Broadcast position to other players
    // This would use Supabase Realtime presence
    await channel.send({
      type: 'broadcast',
      event: 'player_position',
      payload: {
        playerId: players.value.find(p => p.id)?.id,
        position
      }
    })
  }

  /**
   * Leave the room
   */
  const leaveRoom = async () => {
    if (channel) {
      await supabase.removeChannel(channel)
      channel = null
    }

    currentRoom.value = null
    players.value = []
    isConnected.value = false
  }

  // Cleanup on unmount
  onUnmounted(() => {
    leaveRoom()
  })

  return {
    currentRoom,
    players,
    isConnected,
    error,
    joinRoom,
    shareRelicFusion,
    updatePlayerPosition,
    leaveRoom
  }
}


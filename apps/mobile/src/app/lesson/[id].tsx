import { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useStreamMobile } from '@/lib/useStreamMobile';
import { BlockRenderer } from '@/components/blocks/BlockRenderer';
import { ContentBlock } from '@sarathi/api-types/blocks';
import { supabase } from '@/lib/supabase';
import { TutorChat } from '@/components/TutorChat';

export default function LessonScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [blocks, setBlocks] = useState<ContentBlock[]>([]);
  const [token, setToken] = useState<string | null>(null);
  const [chatVisible, setChatVisible] = useState(false);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setToken(data.session?.access_token || null);
    });
  }, []);

  const { startStream, isStreaming } = useStreamMobile({
    url: `${process.env.EXPO_PUBLIC_API_BASE || 'http://localhost:4010/api/v1'}/lessons/${id}/content`,
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    onEvent: (event) => {
      if (event.type === 'block') {
        setBlocks(prev => [...prev, event.block as ContentBlock]);
      }
    },
    onError: (error) => console.error('Stream error:', error),
  });

  useEffect(() => {
    if (token) {
      startStream();
    }
  }, [token, startStream]);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={styles.backButton}>← Back</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => setChatVisible(true)}>
          <Text style={styles.chatButton}>Ask Tutor</Text>
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.scroll}>
        {blocks.map((block) => (
          <BlockRenderer key={block.id} block={block} />
        ))}
        {isStreaming && (
          <View style={styles.loading}>
            <ActivityIndicator size="small" />
            <Text style={styles.loadingText}>Loading content...</Text>
          </View>
        )}
      </ScrollView>

      {chatVisible && (
        <TutorChat lessonId={id as string} onClose={() => setChatVisible(false)} token={token} />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  header: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    padding: 16, 
    borderBottomWidth: 1, 
    borderBottomColor: '#eee' 
  },
  backButton: { fontSize: 16, color: '#007AFF' },
  chatButton: { fontSize: 16, color: '#007AFF', fontWeight: 'bold' },
  scroll: { padding: 20 },
  loading: { flexDirection: 'row', alignItems: 'center', marginVertical: 20, gap: 8 },
  loadingText: { color: '#666' }
});

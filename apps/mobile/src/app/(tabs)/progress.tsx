import { View, Text, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@sarathi/api-client';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function ProgressScreen() {
  const { data: progress, isLoading } = useQuery({
    queryKey: ['me-progress'],
    queryFn: () => apiClient.GET('/api/v1/users/me/progress').then(res => res.data),
  });

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
      </View>
    );
  }


  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.header}>Mastery Progress</Text>
        
        {progress && progress.length === 0 && (
          <Text style={styles.empty}>No progress recorded yet.</Text>
        )}

        {progress?.map((mastery: any) => (
          <View key={mastery.id} style={styles.card}>
            <Text style={styles.conceptName}>{mastery.concept_id}</Text>
            <View style={styles.barBg}>
              <View style={[styles.barFill, { width: `${(parseFloat(mastery.score) / 10) * 100}%` }]} />
            </View>
            <Text style={styles.value}>{parseFloat(mastery.score).toFixed(1)} / 10</Text>
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9f9f9' },
  scroll: { padding: 20, gap: 16 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { fontSize: 24, fontWeight: 'bold', marginBottom: 8 },
  empty: { color: '#666' },
  card: { backgroundColor: '#fff', padding: 16, borderRadius: 12, borderWidth: 1, borderColor: '#eee', gap: 8 },
  conceptName: { fontSize: 16, fontWeight: '600' },
  barBg: { height: 8, backgroundColor: '#eee', borderRadius: 4, overflow: 'hidden' },
  barFill: { height: '100%', backgroundColor: '#000' },
  value: { fontSize: 14, color: '#666', textAlign: 'right' }
});

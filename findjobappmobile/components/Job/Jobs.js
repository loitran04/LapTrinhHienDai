
import 'moment/locale/vi';
import MyStyles from '../../styles/MyStyles';
import API, { endpoints } from '../../configs/API';
import Item from './Item';
import { useEffect, useState } from 'react';
import { useNavigation } from '@react-navigation/native';
import { Alert, FlatList, RefreshControl, StatusBar, View } from 'react-native';
import { ActivityIndicator, Searchbar, Button, Menu } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';

export default Jobs = () => {
  const [categories, setCategories] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [q, setQ] = useState("");
  const [cateId, setCateId] = useState(null);
  const [location, setLocation] = useState(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [showCate, setShowCate] = useState(false);
  const [showLocation, setShowLocation] = useState(false);
  const nav = useNavigation();
  const locations = ['Hồ Chí Minh', 'Hà Nội', 'Đà Nẵng', 'Bình Dương'];
  const loadJobs = async () => {
    if (page <= 0) return;

    setLoading(true);
    let url = `${endpoints['jobs']}?q=${q}&page=${page}`;
    if (cateId) url += `&category_id=${cateId}`;
    if (location) url += `&location=${location}`;
    try {
      const res = await API.get(url);
      const newJobs = res.data.results || res.data;
      setJobs(prev => page === 1 ? newJobs : [...prev, ...newJobs]);
      if (!res.data.next) setPage(0);
    } catch (err) {
      Alert.alert("Lỗi", "Không tải được việc làm");
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const res = await API.get(endpoints['categories']);
      setCategories(res.data);
    } catch (err) {
      console.error("Lỗi load danh mục", err);
    }
  };

  const handleSearch = (text) => {
    setQ(text);
    setPage(1);
  };

  const handleRefresh = () => {
    setPage(1);
    setJobs([]);
  };

  const handleLoadMore = () => {
    if (!loading && page > 0) {
      setPage(prev => prev + 1);
    }
  };

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    const timeout = setTimeout(() => {
      loadJobs();
    }, 500);
    return () => clearTimeout(timeout);
  }, [q, cateId, location, page]);

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#fff' }}>
      <StatusBar backgroundColor="#fff" barStyle="dark-content" />
      <View style={MyStyles.container}>
        <Searchbar
          placeholder="Nhập từ khóa..."
          value={q}
          onChangeText={handleSearch}
        />

        <View style={{ flexDirection: 'row', flexWrap: 'wrap', margin: 10 }}>
          <Menu
            visible={showCate}
            onDismiss={() => setShowCate(false)}
            anchor={
              <Button mode="outlined" onPress={() => setShowCate(true)} style={{ marginRight: 8 }}>
                {cateId ? categories.find(c => c.id === cateId)?.name : "Ngành nghề"}
              </Button>
            }>
            {categories.map(c => (
              <Menu.Item key={c.id} onPress={() => { setCateId(c.id); setPage(1); setShowCate(false); }} title={c.name} />
            ))}
          </Menu>

          <Menu
            visible={showLocation}
            onDismiss={() => setShowLocation(false)}
            anchor={
              <Button mode="outlined" onPress={() => setShowLocation(true)}>
                {location || "Địa điểm"}
              </Button>
            }>
            {locations.map(loc => (
              <Menu.Item key={loc} onPress={() => { setLocation(loc); setPage(1); setShowLocation(false); }} title={loc} />
            ))}
          </Menu>
        </View>

        <FlatList
          data={jobs}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <Item
              instance={item}
              onPress={() => nav.navigate('JobDetails', { job: item })}
            />
          )}
          refreshControl={<RefreshControl refreshing={loading} onRefresh={handleRefresh} />}
          onEndReached={handleLoadMore}
          onEndReachedThreshold={0.5}
          ListFooterComponent={loading && <ActivityIndicator />}
        />
      </View>
    </SafeAreaView>
  );
};

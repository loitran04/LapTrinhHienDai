import { useEffect, useState } from 'react';
import { Alert, FlatList, View, Text, Linking } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ActivityIndicator, Button, Card, TextInput } from 'react-native-paper';
import AsyncStorage from '@react-native-async-storage/async-storage';
import API, { authApis, endpoints } from '../../configs/API';
import moment from 'moment';
import MyStyles from '../../styles/MyStyles';

const ApplicationCard = ({ item }) => {
  const [newCV, setNewCV] = useState(item.cv_link || "");
  const [updating, setUpdating] = useState(false);

  const updateCV = async () => {
    try {
      setUpdating(true);
      const token = await AsyncStorage.getItem("access_token");
      const res = await authApis(token).patch(endpoints['apply-details'](item.id), {
        cv_link: newCV
      });
      Alert.alert("Cập nhật CV thành công!");
    } catch (err) {
      console.error("Lỗi cập nhật CV:", err.response?.data || err.message);
      Alert.alert("Lỗi", "Không thể cập nhật CV.");
    } finally {
      setUpdating(false);
    }
  };

  const renderStatus = (status) => {
    switch (status) {
      case 'pending': return "⏳ Đang chờ duyệt";
      case 'approved': return "✅ Đã được chấp nhận";
      case 'rejected': return "❌ Bị từ chối";
      default: return "🔄 Không xác định";
    }
  };

  return (
    <Card style={[MyStyles.mar, { borderRadius: 12 }]}>
      <Card.Title title={item.job_title} titleStyle={{ fontWeight: "bold", fontSize: 16 }}/>
      <Card.Content>
        <Text>Trạng thái: {renderStatus(item.status)}</Text>
        <Text>Thời gian ứng tuyển: {moment(item.applied_date).fromNow()}</Text>

        {item.status === "pending" ? (
          <>
            <TextInput
              label="Link CV mới"
              value={newCV}
              onChangeText={setNewCV}
              mode="outlined"
              style={{ marginVertical: 8 }}
            />
            <Button
              loading={updating}
              icon="content-save-edit"
              mode="contained"
              onPress={updateCV}
            >
              Cập nhật CV
            </Button>
          </>
        ) : (
          <Button mode="outlined" onPress={() => Linking.openURL(item.cv_link)}>
            Xem CV
          </Button>
        )}
      </Card.Content>
    </Card>
  );
};

const MyApplications = () => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

const loadApplications = async () => {
  try {
    const token = await AsyncStorage.getItem('access_token');
    if (!token) {
      Alert.alert("Chưa đăng nhập", "Vui lòng đăng nhập lại!");
      setLoading(false);
      return;
    }

    const res = await authApis(token).get(endpoints['apply']);
    const applyList = res.data;

    // Gọi song song các job details
    const withJobTitles = await Promise.all(
      applyList.map(async (a) => {
        try {
          const jobRes = await API.get(endpoints["job-details"](a.job_id));
          return { ...a, job_title: jobRes.data.title || "(Không có tiêu đề)" };
        } catch (error) {
          console.error("Lỗi lấy job:", error);
          return { ...a, job_title: "(Không có tiêu đề)" };
        }
      })
    );

    setApplications(withJobTitles);
  } catch (err) {
    Alert.alert("Lỗi", "Không thể tải danh sách ứng tuyển.");
  } finally {
    setLoading(false);
  }
};


  useEffect(() => {
    loadApplications();
  }, []);

  return (
    <SafeAreaView style={MyStyles.container}>
      {loading ? (
        <ActivityIndicator />
      ) : applications.length === 0 ? (
        <Text style={{ textAlign: 'center', marginTop: 20 }}>
          Không có đơn ứng tuyển nào
        </Text>
      ) : (
        <>
          <FlatList
            data={applications}
            renderItem={({ item }) => <ApplicationCard item={item} />}
            keyExtractor={item => item.id.toString()}
          />
        </>
      )}
    </SafeAreaView>
  );
};

export default MyApplications;
import React, { useContext, useEffect, useState } from 'react';
import { ScrollView, Text, View, StatusBar, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { Button } from 'react-native-paper';
import MyStyles from '../../styles/MyStyles';
import he from 'he';
import API, { authApis, endpoints } from '../../configs/API';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { MyUserContext } from '../../configs/Contexts';

const JobDetails = ({ route }) => {
  const { job } = route.params;
  const nav = useNavigation();
  const user = useContext(MyUserContext);
  const [isFollowing, setIsFollowing] = useState(false);

  const applyJob = async () => {
    try {
      const token = await AsyncStorage.getItem("access_token");
      if (!token) {
        Alert.alert("Thông báo", "Vui lòng đăng nhập để ứng tuyển!");
        return;
      }
      const profileRes = await authApis(token).get(endpoints["current-candidate"]);
      const cv_link = profileRes.data.cv_link;
  
      if (!cv_link) {
        Alert.alert("Lỗi", "Bạn chưa cập nhật đường dẫn CV. Vui lòng cập nhật hồ sơ!");
        return;
      }
      const res = await authApis(token).post(endpoints["apply"], {
        job_id: job.id,
        cv_link: cv_link
      });
      if (res.status === 201) {
        Alert.alert("Thành công", "Bạn đã ứng tuyển thành công!");
      }
    } catch (err) {
      console.error("Lỗi ứng tuyển:", err.response?.data || err.message);
      Alert.alert("Thất bại", "Ứng tuyển không thành công. Vui lòng kiểm tra lại!");
    }
  };

  const checkFollowStatus = async () => {
    try {
      const token = await AsyncStorage.getItem("access_token");
      if (!token || !user || user.role !== "candidate") return;

      const res = await authApis(token).get(endpoints["follow"]);
      const followed = res.data.some(f => f.employer_id === job.employer_id);
      setIsFollowing(followed);
    } catch (err) {
      console.error("Lỗi kiểm tra theo dõi:", err);
    }
  };

  const toggleFollow = async () => {
    try {
      const token = await AsyncStorage.getItem("access_token");
      if (!token || !user || user.role !== "candidate") {
        Alert.alert("Thông báo", "Chỉ ứng viên mới có thể theo dõi công ty.");
        return;
      }
      if (isFollowing) {
        await authApis(token).delete(endpoints["unfollow"] + `?employer_id=${job.employer_id}`);
        setIsFollowing(false);
      } else {
        await authApis(token).post(endpoints["follow"], { employer_id: job.employer_id });
        setIsFollowing(true);
      }
    } catch (err) {
      console.error("Lỗi toggle theo dõi:", err);
    }
  };

  useEffect(() => {
    checkFollowStatus();
  }, []);

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#fff' }}>
      <StatusBar backgroundColor="#fff" barStyle="dark-content" />
      <View style={MyStyles.wrapper}>
        <ScrollView contentContainerStyle={MyStyles.scroll}>
          <Text style={[MyStyles.subject, { marginBottom: 10 }]}>{job.title}</Text>

          <View style={MyStyles.card}>
            <Text style={MyStyles.info}>📍 Địa điểm: {job.location}</Text>
            <Text style={MyStyles.info}>💰 Lương: {job.salary} đ</Text>
            <Text style={MyStyles.info}>🕒 Giờ làm: {job.work_hours} giờ</Text>
            <Text style={MyStyles.info}>🧠 Kỹ năng: {job.skills}</Text>
          </View>

          <Text style={[MyStyles.subject, { marginBottom: 8 }]}>📝 Mô tả</Text>
          <Text style={[MyStyles.info, MyStyles.textarea]}>
            {he.decode(job.description.replace(/<[^>]*>/g, ''))}
          </Text>

          <Button
            icon="send"
            mode="contained"
            onPress={applyJob}
            style={{ marginTop: 20 }}
          >
            Ứng tuyển ngay
          </Button>

          {user?.role === "candidate" && (
            <Button
              icon={isFollowing ? "heart-off" : "heart"}
              mode="outlined"
              onPress={toggleFollow}
              style={{ marginTop: 10 }}
            >
              {isFollowing ? "Bỏ theo dõi công ty" : "Theo dõi công ty"}
            </Button>
          )}
        </ScrollView>
      </View>
    </SafeAreaView>
  );
};

export default JobDetails;

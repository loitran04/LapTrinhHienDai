import { useState, useEffect } from "react";
import { KeyboardAvoidingView, Platform, ScrollView, View, Alert } from "react-native";
import { Icon } from "react-native-paper";
import { useNavigation } from "@react-navigation/native";
import { SafeAreaView } from "react-native-safe-area-context";
import MyStyles from "../../styles/MyStyles";
import API, { authApis, endpoints } from "../../configs/API";
import MyInput, { MyButton, validateInput } from "../User/MyInput";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { changeState } from "../../configs/Utils";

const PostJob = () => {
  const [job, setJob] = useState({});
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState({});
  const [enabled, setEnabled] = useState(true);
  const nav = useNavigation();

  const fields = {
    title: { label: "Tiêu đề", icon: "format-title", required: "Vui lòng nhập tiêu đề!" },
    description: { label: "Mô tả", icon: "text-box-outline", required: "Vui lòng nhập mô tả!" },
    skills: { label: "Kỹ năng", icon: "star-outline", required: "Vui lòng nhập kỹ năng!" },
    salary: { label: "Lương", icon: "cash", required: "Vui lòng nhập lương!" },
    location: { label: "Địa điểm", icon: "map-marker", required: "Vui lòng nhập địa điểm!" },
    work_hours: { label: "Giờ làm việc", icon: "clock-outline", required: "Vui lòng nhập giờ làm việc!", type: "number" },
    category_id: {
      label: "Ngành nghề",
      icon: "shape-outline",
      type: "select",
      options: categories.map(c => ({ label: c.name, value: c.id })),
      required: "Chọn ngành nghề!"
    }
  };

  const validate = () => validateInput(job, setError, "required", fields);

  const loadCategories = async () => {
    try {
      const res = await API.get(endpoints["categories"]);
      setCategories(res.data);
    } catch (err) {
      console.error("Lỗi load danh mục", err);
    }
  };

  useEffect(() => {
    loadCategories();
  }, []);

const postJob = async () => {
  if (validate() === true) {
    try {
      setEnabled(false);
      const token = await AsyncStorage.getItem("access_token");
      if (!token) throw new Error("Không có access_token!");
      const res = await authApis(token).post(endpoints["jobs"], job);

      if (res.status === 201) {
        Alert.alert("Thành công", "Tin tuyển dụng đã được đăng!");
        nav.goBack();
      }
    } catch (err) {
      Alert.alert("Lỗi", "Không thể đăng job. Kiểm tra lại thông tin hoặc đăng nhập lại!");
    } finally {
      setEnabled(true);
    }
  }
};

  const reset = () => {
    Object.keys(job).forEach(k => changeState(setJob, k, ""));
  };

  return (
    <SafeAreaView style={MyStyles.container}>
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : "height"}>
        <ScrollView>
          <View style={MyStyles.aSelfCenter}>
            <Icon source="clipboard-plus" size={150} color="#530065" />
          </View>
          {Object.keys(fields).map(k => (
            <MyInput key={k} field={k} setState={setJob} value={job[k]} error={error[k]} {...fields[k]} />
          ))}
        </ScrollView>
        <View style={[MyStyles.row, MyStyles.flexEnd]}>
          <MyButton icon="refresh" onPress={reset} label="Nhập lại" />
          <MyButton icon="check" onPress={postJob} label="Đăng tin" enabled={enabled} />
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

export default PostJob;

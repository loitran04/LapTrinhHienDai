import { useState } from "react";
import { KeyboardAvoidingView, Platform, ScrollView, View, Alert, Text, Image } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Icon } from "react-native-paper";
import * as ImagePicker from 'expo-image-picker';
import { useNavigation } from "@react-navigation/native";
import MyStyles from "../../styles/MyStyles";
import MyInput, { MyButton, validateInput } from "./MyInput";
import API, { endpoints } from "../../configs/API";

const RegisterEmployer = () => {
  const [employer, setEmployer] = useState({});
  const [error, setError] = useState({});
  const [images, setImages] = useState([]);
  const [enabled, setEnabled] = useState(true);
  const nav = useNavigation();

  const fields = {
    name: { label: "Tên công ty", icon: "domain", required: "Vui lòng nhập tên!" },
    tax_code: { label: "Mã số thuế", icon: "barcode", required: "Vui lòng nhập mã số thuế!" },
    location: { label: "Địa chỉ", icon: "map-marker", required: "Vui lòng nhập địa chỉ!" },
    email: { label: "Email", icon: "email", required: "Vui lòng nhập email!" },
    username: { label: "Tên đăng nhập", icon: "account", required: "Vui lòng nhập tên đăng nhập!" },
    password: { label: "Mật khẩu", icon: "lock", required: "Vui lòng nhập mật khẩu!", secure: true },
    confirm_password: { label: "Xác nhận mật khẩu", icon: "lock", required: "Vui lòng xác nhận mật khẩu!", secure: true, match: "password" },
    avatar: { label: "Ảnh đại diện", icon: "image", type: "image" },
  };

  const pickMultipleImages = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsMultipleSelection: true,
      selectionLimit: 5,
      quality: 1
    });

    if (!result.canceled) {
      setImages(result.assets || []);
    }
  };

  const validate = () => {
    let valid = validateInput(employer, setError, "required", fields);
    if (images.length < 3) {
      Alert.alert("Thiếu ảnh", "Vui lòng chọn ít nhất 3 ảnh môi trường!");
      return false;
    }
    return valid;
  };

  const register = async () => {
    if (!validate()) return;

    try {
      setEnabled(false);
      const form = new FormData();

      for (let key of Object.keys(employer)) {
        if (key === "avatar" && employer.avatar) {
          form.append("avatar", {
            uri: employer.avatar.uri,
            type: "image/jpeg",
            name: employer.avatar.fileName || "avatar.jpg"
          });
        } else if (key !== "confirm_password") {

          form.append(key, employer[key]);
        }
      }

      images.forEach((img) => {
        form.append("images", {
          uri: img.uri,
          type: "image/jpeg",
          name: img.fileName || "work.jpg"
        });
      });

      const res = await API.post(endpoints["register-employer"], form, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      if (res.status === 201) {
        Alert.alert("Thành công", "Đăng ký thành công, vui lòng đăng nhập!");
        nav.navigate("Login");
      }
    } catch (err) {
      console.error("Lỗi đăng ký:", err);
      Alert.alert("Lỗi", "Không thể đăng ký, kiểm tra lại thông tin!");
    } finally {
      setEnabled(true);
    }
  };

  const reset = () => {
    setEmployer({});
    setImages([]);
  };

  return (
    <SafeAreaView style={MyStyles.container}>
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : "height"}>
        <ScrollView>
          <View style={MyStyles.aSelfCenter}>
            <Icon source="briefcase-account" size={160} color="#530065" />
          </View>

          {Object.keys(fields).map((k) => (
            <MyInput
              key={k}
              field={k}
              setState={setEmployer}
              value={employer[k]}
              error={error[k]}
              {...fields[k]}
            />
          ))}

          <MyButton icon="image-multiple" label="Chọn ảnh môi trường" onPress={pickMultipleImages} />
          <Text style={{ marginHorizontal: 10 }}>{images.length} ảnh môi trường đã chọn</Text>
          <ScrollView horizontal style={{ marginHorizontal: 10 }}>
            {images.map((img, idx) => (
              <Image key={idx} source={{ uri: img.uri }} style={{ width: 80, height: 80, margin: 4, borderRadius: 10 }} />
            ))}
          </ScrollView>
        </ScrollView>

        <View style={[MyStyles.row, MyStyles.flexEnd]}>
          <MyButton icon="refresh" onPress={reset} label="Nhập lại" />
          <MyButton icon="account" onPress={register} label="Đăng ký" enabled={enabled} />
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

export default RegisterEmployer;

import React from 'react';
import { View, Text, StatusBar } from 'react-native';
import { MyButton } from './MyInput';
import MyStyles from '../../styles/MyStyles';
import { useNavigation } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';

const SelectRole = () => {
  const nav = useNavigation();

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#fff' }}>
    <StatusBar backgroundColor="#fff" barStyle="dark-content" />
    <View style={[MyStyles.container, MyStyles.aSelfCenter]}>
      <Text style={MyStyles.subject}>Bạn muốn đăng ký với vai trò:</Text>
      <MyButton label="Ứng viên" icon="account" onPress={() => nav.navigate("RegisterCandidate")} />
      <MyButton label="Nhà tuyển dụng" icon="account-tie" onPress={() => nav.navigate("RegisterEmployer")} />
    </View>
    </SafeAreaView>
  );
};

export default SelectRole;
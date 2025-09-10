import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useContext } from 'react';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useNavigation } from '@react-navigation/native';
import { IconButton } from 'react-native-paper';
import { MyUserContext } from './Contexts';
import Jobs from '../components/Job/Jobs';
import JobDetails from '../components/Job/JobDetails';
import Login from '../components/User/Login';
import SelectRole from '../components/User/SelectRole';
import RegisterCandidate from '../components/User/RegisterCandidate';
import RegisterEmployer from '../components/User/RegisterEmployer';
import MyApplications from '../components/Job/MyApplications';
import Profile from '../components/User/Profile';
import PostJob from '../components/Job/PostJob';
import JobList from '../components/Job/JobList';
import Applicants from '../components/Job/Applicants';
import AdminStats from '../components/Job/AdminStats';
import AdminVerifications from '../components/User/AdminVerifications';

// Stack navigator
const Stack = createNativeStackNavigator();

export const MyStack = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Main" component={MyTab} />
      <Stack.Screen name="JobDetails" component={JobDetails} options={{ headerShown: true, title: 'Chi tiết  công việc' }} />
      <Stack.Screen name="SelectRole" component={SelectRole} />
      <Stack.Screen name="PostJob" component={PostJob} />
      <Stack.Screen name="Applicants" component={Applicants} options={{headerShown: true, title: 'Danh sách ứng viên'}}/>
      <Stack.Screen name="JobList" component={JobList} />
      <Stack.Screen name="AdminStarts" component={AdminStats} options={{ headerShown: true, title: "Thống kê" }}/>
      <Stack.Screen name="AdminVerifications" component={AdminVerifications} options={{ title: "Xét duyệt" }}/>
      <Stack.Screen name="RegisterCandidate" component={RegisterCandidate} options={{ headerShown: true, title: 'Đăng ký Ứng viên' }} />
      <Stack.Screen name="RegisterEmployer" component={RegisterEmployer} options={{ headerShown: true, title: 'Đăng ký Nhà tuyển dụng' }} />
      <Stack.Screen name="Login" component={Login} options={{ headerShown: true, title: 'Đăng nhập' }} />
    </Stack.Navigator>
  );
};

// Tab Navigator
const Tab = createBottomTabNavigator();

const tabOptions = (title, icon, size, color) => {
  return {
    title: title,
    tabBarIcon: () => <Icon name={icon} size={size} color={color} />
  };
};

const getTabsByRole = (role) => {
  switch (role) {
    case 'candidate':
      return [
        { order: 1, name: 'Trang chủ', component: Jobs, title: 'Việc làm', icon: 'home' },
        { order: 2, name: 'Việc của tôi', component: MyApplications, title: 'Việc của tôi', icon: 'briefcase' },
        { order: 3, name: 'Cá nhân', component: Profile, title: 'Cá nhân', icon: 'account' },
      ];
    case 'employer':
      return [
        { order: 1, name: 'Trang chủ', component: Jobs, title: 'Trang chủ', icon: 'home' },
        { order: 2, name: 'Đăng tin', component: PostJob, title: 'Đăng tin', icon: 'plus-box' },
        { order: 3, name: 'Quản lý', component: JobList, title: 'Quản lý', icon: 'clipboard-list' },
        { order: 4, name: 'Cá nhân', component: Profile, title: 'Cá nhân', icon: 'account' },
      ];
    case 'admin':
      return [
        { order: 1, name: 'Xét duyệt', component: AdminVerifications, title: 'Xét duyệt', icon: 'clipboard-check-outline' },
        { order: 2, name: 'Thống kê', component: AdminStats, title: 'Thống kê', icon: 'chart-bar' },
        { order: 3, name: 'Cá nhân', component: Profile, title: 'Cá nhân', icon: 'account' },
      ];
    default:
      return [
        { order: 1, name: 'Trang chủ', component: Jobs, title: 'Trang chủ', icon: 'home' },
        { order: 2, name: 'Đăng ký', component: SelectRole, title: 'Đăng ký', icon: 'account-plus' },
        { order: 3, name: 'Đăng nhập', component: Login, title: 'Đăng nhập', icon: 'login' },
      ];
  }
};

export const MyTab = ({ size = 28, color = '#0066CC' }) => {
  const user = useContext(MyUserContext);
  const nav = useNavigation();

  const screenOptions = {
    headerShown: false,
    headerLeft: () =>
      nav.canGoBack() ? (
        <IconButton icon="arrow-left" onPress={() => nav.goBack()} />
      ) : null
  };

  const filteredTabs = getTabsByRole(user?.role);

  return (
    <Tab.Navigator backBehavior="order" screenOptions={screenOptions}>
      {filteredTabs.map(t => (
        <Tab.Screen
          key={t.order}
          name={t.name}
          component={t.component}
          options={tabOptions(t.title, t.icon, size, color)}
        />
      ))}
    </Tab.Navigator>
  );
};
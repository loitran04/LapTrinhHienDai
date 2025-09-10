import { NavigationContainer } from '@react-navigation/native';
import { MyDispatchContext, MyUserContext } from './configs/Contexts';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { StatusBar } from 'react-native';
import { MyStack} from './configs/Routes';
import { useReducer} from 'react';
import { Provider as PaperProvider } from 'react-native-paper';
import { MyUserReducer } from './reducers/MyUserReducer';

export default function App() {
  const [user, dispatch] = useReducer(MyUserReducer, null);

  return (
    <MyUserContext.Provider value={user}>
      <MyDispatchContext.Provider value={dispatch}>
        <SafeAreaProvider>
          <PaperProvider>
            <StatusBar backgroundColor="#fff" barStyle="dark-content" />
            <NavigationContainer>
              <MyStack />
            </NavigationContainer>
          </PaperProvider>
        </SafeAreaProvider>
      </MyDispatchContext.Provider>
    </MyUserContext.Provider>
  );
}


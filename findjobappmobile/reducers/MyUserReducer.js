export const MyUserReducer = (status, action) => {
    switch (action.type) {
        case 'login':
            return action.payload;
        case 'logout':
            return null;
    }
    return status;
};
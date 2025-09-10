export const changeState = (setState, key, value) => {
    if (key)
        setState(current => { return {...current, [key]: value} });
    else 
        setState(value);
}
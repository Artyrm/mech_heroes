
// Вставь этот фрагмент в свой Tampermonkey скрипт внутри перехватчика fetch
const origFetch = window.fetch;
window.fetch = async (...args) => {
    let response = await origFetch(...args);
    
    // Если сервер вернул 400/500 с текстом HashMismatch
    if (!response.ok) {
        const text = await response.clone().text();
        if (text.includes("Hash") && text.includes("mismatch")) {
            const match = text.match(/expected (-?\d+)/);
            if (match) {
                console.log("!!! Успешно перехвачен хеш:", match[1]);
                // Здесь логика подмены: 
                // 1. Повторяем запрос с правильным хешем
                // 2. Отдаем результат в Unity как будто это был первый запрос
            }
        }
    }
    return response;
};

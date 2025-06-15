// composables/ui/useSnackbar.js

import { ref, reactive } from 'vue';

/**
 * スナックバー通知を管理するComposable
 * 
 * 機能:
 * - 成功・エラー・警告・情報メッセージの表示
 * - メッセージの自動非表示
 * - 複数メッセージのキュー管理
 * - カスタムアクション付きメッセージ
 * 
 * 使用例:
 * const { showSuccess, showError, showWarning, showInfo, snackbar } = useSnackbar();
 * showSuccess('保存が完了しました');
 * showError('エラーが発生しました');
 */
export function useSnackbar() {
    // スナックバーの基本状態
    const snackbar = reactive({
        show: false,
        text: '',
        color: 'success',
        timeout: 3000,
        multiline: false,
        vertical: false,
        actions: []
    });

    // メッセージキュー（複数のメッセージを順番に表示）
    const messageQueue = ref([]);
    const isProcessingQueue = ref(false);

    // スナックバーの色とアイコンの定義
    const messageTypes = {
        success: {
            color: 'success',
            icon: 'mdi-check-circle',
            timeout: 3000
        },
        error: {
            color: 'error',
            icon: 'mdi-alert-circle',
            timeout: 5000
        },
        warning: {
            color: 'warning',
            icon: 'mdi-alert',
            timeout: 4000
        },
        info: {
            color: 'info',
            icon: 'mdi-information',
            timeout: 3000
        }
    };

    /**
     * スナックバーを表示する基本関数
     * @param {Object} options - スナックバーの設定オプション
     * @param {string} options.text - 表示するメッセージ
     * @param {string} options.color - スナックバーの色
     * @param {number} options.timeout - 自動非表示までの時間（ms）
     * @param {boolean} options.multiline - 複数行表示かどうか
     * @param {boolean} options.vertical - 縦配置かどうか
     * @param {Array} options.actions - アクションボタンの配列
     */
    const showSnackbar = (options) => {
        // デフォルト値との合成
        const config = {
            show: true,
            text: '',
            color: 'success',
            timeout: 3000,
            multiline: false,
            vertical: false,
            actions: [],
            ...options
        };

        // スナックバーの状態を更新
        Object.assign(snackbar, config);
    };

    /**
     * 成功メッセージを表示
     * @param {string} message - 表示するメッセージ
     * @param {Object} options - 追加オプション
     */
    const showSuccess = (message, options = {}) => {
        showSnackbar({
            text: message,
            color: messageTypes.success.color,
            timeout: messageTypes.success.timeout,
            ...options
        });
    };

    /**
     * エラーメッセージを表示
     * @param {string} message - 表示するメッセージ
     * @param {Object} options - 追加オプション
     */
    const showError = (message, options = {}) => {
        showSnackbar({
            text: message,
            color: messageTypes.error.color,
            timeout: messageTypes.error.timeout,
            ...options
        });
    };

    /**
     * 警告メッセージを表示
     * @param {string} message - 表示するメッセージ
     * @param {Object} options - 追加オプション
     */
    const showWarning = (message, options = {}) => {
        showSnackbar({
            text: message,
            color: messageTypes.warning.color,
            timeout: messageTypes.warning.timeout,
            ...options
        });
    };

    /**
     * 情報メッセージを表示
     * @param {string} message - 表示するメッセージ
     * @param {Object} options - 追加オプション
     */
    const showInfo = (message, options = {}) => {
        showSnackbar({
            text: message,
            color: messageTypes.info.color,
            timeout: messageTypes.info.timeout,
            ...options
        });
    };

    /**
     * アクション付きメッセージを表示
     * @param {string} message - 表示するメッセージ
     * @param {Array} actions - アクションボタンの配列
     * @param {Object} options - 追加オプション
     */
    const showWithActions = (message, actions = [], options = {}) => {
        showSnackbar({
            text: message,
            actions: actions.map(action => ({
                text: action.text || 'アクション',
                color: action.color || 'white',
                handler: action.handler || (() => { }),
                ...action
            })),
            timeout: 0, // アクション付きの場合は自動非表示しない
            ...options
        });
    };

    /**
     * 確認付きメッセージを表示（元に戻す機能付き）
     * @param {string} message - 表示するメッセージ
     * @param {Function} undoCallback - 元に戻す処理
     * @param {Object} options - 追加オプション
     */
    const showWithUndo = (message, undoCallback, options = {}) => {
        showWithActions(
            message,
            [
                {
                    text: '元に戻す',
                    color: 'white',
                    handler: () => {
                        undoCallback();
                        hideSnackbar();
                    }
                }
            ],
            {
                color: 'info',
                timeout: 10000, // 10秒間表示
                ...options
            }
        );
    };

    /**
     * API操作の結果に基づいてメッセージを表示
     * @param {Object} response - APIレスポンス
     * @param {string} successMessage - 成功時のメッセージ（省略可）
     * @param {string} errorMessage - エラー時のメッセージ（省略可）
     */
    const showApiResult = (response, successMessage = null, errorMessage = null) => {
        if (response && response.success) {
            // 成功時
            const message = successMessage || response.message || '操作が完了しました';
            showSuccess(message);
        } else {
            // エラー時
            const message = errorMessage || response?.message || '操作中にエラーが発生しました';
            showError(message);
        }
    };

    /**
     * ローディング中のメッセージを表示
     * @param {string} message - 表示するメッセージ
     * @param {Object} options - 追加オプション
     */
    const showLoading = (message = '処理中...', options = {}) => {
        showSnackbar({
            text: message,
            color: 'primary',
            timeout: 0, // 手動で閉じるまで表示
            actions: [], // アクションボタンなし
            ...options
        });
    };

    /**
     * スナックバーを非表示にする
     */
    const hideSnackbar = () => {
        snackbar.show = false;

        // キューに次のメッセージがあれば処理
        processQueue();
    };

    /**
     * メッセージをキューに追加
     * @param {Object} options - スナックバーの設定オプション
     */
    const queueMessage = (options) => {
        messageQueue.value.push(options);

        if (!isProcessingQueue.value) {
            processQueue();
        }
    };

    /**
     * メッセージキューを処理
     */
    const processQueue = () => {
        if (messageQueue.value.length === 0) {
            isProcessingQueue.value = false;
            return;
        }

        if (snackbar.show) {
            // 現在表示中の場合は少し待つ
            setTimeout(processQueue, 500);
            return;
        }

        isProcessingQueue.value = true;
        const nextMessage = messageQueue.value.shift();
        showSnackbar(nextMessage);
    };

    /**
     * キューに追加して成功メッセージを表示
     * @param {string} message - 表示するメッセージ
     * @param {Object} options - 追加オプション
     */
    const queueSuccess = (message, options = {}) => {
        queueMessage({
            text: message,
            color: messageTypes.success.color,
            timeout: messageTypes.success.timeout,
            ...options
        });
    };

    /**
     * キューに追加してエラーメッセージを表示
     * @param {string} message - 表示するメッセージ
     * @param {Object} options - 追加オプション
     */
    const queueError = (message, options = {}) => {
        queueMessage({
            text: message,
            color: messageTypes.error.color,
            timeout: messageTypes.error.timeout,
            ...options
        });
    };

    /**
     * 複数のメッセージを一度に表示（改行区切り）
     * @param {Array} messages - メッセージの配列
     * @param {string} type - メッセージタイプ（success, error, warning, info）
     * @param {Object} options - 追加オプション
     */
    const showMultiple = (messages, type = 'info', options = {}) => {
        if (!Array.isArray(messages) || messages.length === 0) return;

        const messageText = messages.join('\n');
        const messageType = messageTypes[type] || messageTypes.info;

        showSnackbar({
            text: messageText,
            color: messageType.color,
            timeout: messageType.timeout + (messages.length * 1000), // メッセージ数に応じてタイムアウトを延長
            multiline: true,
            ...options
        });
    };

    /**
     * カスタムスタイルでメッセージを表示
     * @param {string} message - 表示するメッセージ
     * @param {Object} customStyle - カスタムスタイル設定
     */
    const showCustom = (message, customStyle = {}) => {
        showSnackbar({
            text: message,
            ...customStyle
        });
    };

    /**
     * バリデーションエラーを表示
     * @param {Object} errors - エラーオブジェクト（フィールド名: エラーメッセージ）
     * @param {Object} options - 追加オプション
     */
    const showValidationErrors = (errors, options = {}) => {
        if (!errors || typeof errors !== 'object') return;

        const errorMessages = Object.values(errors)
            .flat()
            .filter(msg => msg && typeof msg === 'string');

        if (errorMessages.length > 0) {
            showMultiple(errorMessages, 'error', {
                timeout: 6000,
                ...options
            });
        }
    };

    /**
     * メッセージキューをクリア
     */
    const clearQueue = () => {
        messageQueue.value = [];
        isProcessingQueue.value = false;
    };

    /**
     * 現在のスナックバーを強制的に閉じる
     */
    const forceClose = () => {
        snackbar.show = false;
        clearQueue();
    };

    // 公開するAPI
    return {
        // 状態
        snackbar,
        messageQueue: messageQueue.value,
        isProcessingQueue,

        // 基本メソッド
        showSnackbar,
        hideSnackbar,

        // タイプ別メソッド
        showSuccess,
        showError,
        showWarning,
        showInfo,

        // 特殊メソッド
        showWithActions,
        showWithUndo,
        showApiResult,
        showLoading,
        showMultiple,
        showCustom,
        showValidationErrors,

        // キュー管理
        queueMessage,
        queueSuccess,
        queueError,
        processQueue,
        clearQueue,

        // ユーティリティ
        forceClose,

        // メッセージタイプ定義（参照用）
        messageTypes
    };
}
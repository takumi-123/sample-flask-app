// 画面の読み込みが終わった後に実行する
document.addEventListener("DOMContentLoaded", function () {
  // ==========================================
  // ① 削除ボタンの確認処理
  // ==========================================
  const deleteButtons = document.querySelectorAll(".delete-btn");

  deleteButtons.forEach(function (button) {
    button.addEventListener("click", function (event) {
      const ok = confirm("本当にこのメッセージを削除しますか？");
      if (!ok) {
        event.preventDefault();
      }
    });
  });

  // ==========================================
  // ② 編集フォームの確認処理
  // ==========================================
  const editForm = document.querySelector(".edit-form");

  if (editForm) {
    editForm.addEventListener("submit", function (event) {
      const ok = confirm("この内容でよろしいですか？");
      if (!ok) {
        event.preventDefault();
      }
    });
  }

  // ダークカード切り替えボタン
  const darkModeButton = document.querySelector("#dark-mode-btn");

  // ダークモードボタンクリックしたら
  if (darkModeButton) {
    darkModeButton.addEventListener("click", function () {
      // bodyタグのクラスを付け加えたりする
      document.body.classList.toggle("dark-mode");
    });
  }
  // 文字数を記録する
  const messageInput = document.querySelector("#message-input");
  const charCount = document.querySelector("#char-count");

  // ２つあったら、ユーザーが文字を打つ瞬間
  if (messageInput && charCount) {
    messageInput.addEventListener("input", function () {
      // テキストエリア(messageInput)に入力された中身(value)を取り出して文字の長さ(length)をかく
      const currentLength = messageInput.value.length;
      // charCountを上の変数に書き換える
      charCount.textContent = currentLength;

      if (currentLength > 140) {
        charCount.style.color = "red";
      } else {
        charCount.style.color = "black";
      }
    });
  }
});

<?php
require "config.php";

$API = "https://api.telegram.org/bot$BOT_TOKEN/";

if (!is_dir("downloads")) {
    mkdir("downloads", 0777, true);
}

function api($method, $data = []) {
    global $API;

    $ch = curl_init($API . $method);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);

    if (!empty($data)) {
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    }

    $res = curl_exec($ch);
    curl_close($ch);

    return json_decode($res, true);
}

function is_subscribed($user_id) {
    global $FORCE_CHANNEL;

    $res = api("getChatMember", [
        "chat_id" => "@".$FORCE_CHANNEL,
        "user_id" => $user_id
    ]);

    if (!isset($res["ok"]) || !$res["ok"]) {
        return true;
    }

    $status = $res["result"]["status"];
    return in_array($status, ["member", "administrator", "creator"]);
}

function blue_button($text, $url) {
    return [
        "text" => $text,
        "url" => $url,
        "style" => "primary"
    ];
}

function main_keyboard() {
    global $BOT_USERNAME, $DEV_USERNAME, $FORCE_CHANNEL;

    return json_encode([
        "inline_keyboard" => [
            [
                blue_button("اضفني للكروب", "https://t.me/$BOT_USERNAME?startgroup=true")
            ],
            [
                blue_button("المطور", "https://t.me/$DEV_USERNAME"),
                blue_button("شراء بوت مشابه", "https://t.me/$DEV_USERNAME")
            ],
            [
                blue_button("قناة البوت", "https://t.me/$FORCE_CHANNEL")
            ]
        ]
    ], JSON_UNESCAPED_UNICODE);
}

function sub_keyboard() {
    global $FORCE_CHANNEL;

    return json_encode([
        "inline_keyboard" => [
            [
                blue_button("اشترك بالقناة", "https://t.me/$FORCE_CHANNEL")
            ]
        ]
    ], JSON_UNESCAPED_UNICODE);
}

function start_text() {
    global $DEV_USERNAME;

    return "• هلا بك في بوت ميوزك 🎧\n\n".
           "• اضفني للكروب وارفعني مشرف\n\n".
           "• اكتب:\n".
           "يوت اسم الاغنية\n".
           "تشغيل اسم الاغنية\n\n".
           "• مثال:\n".
           "يوت فيروز\n\n".
           "• المطور: @$DEV_USERNAME";
}

function clean_name($name) {
    $name = preg_replace('/[\\\\\/\:\*\?\"\<\>\|]/', '', $name);
    return mb_substr($name, 0, 80);
}

function download_audio($query) {
    $out = "downloads/%(title)s.%(ext)s";

    $cmd = "yt-dlp --cookies cookies.txt --no-playlist --format bestaudio ".
           "--socket-timeout 15 --retries 3 ".
           "-o ".escapeshellarg($out)." ".
           escapeshellarg("ytsearch5:$query").
           " 2>&1";

    $output = shell_exec($cmd);

    $files = glob("downloads/*");
    if (!$files || count($files) == 0) {
        throw new Exception($output ?: "فشل التحميل");
    }

    usort($files, function($a, $b) {
        return filemtime($b) - filemtime($a);
    });

    $file = $files[0];
    $title = clean_name(pathinfo($file, PATHINFO_FILENAME));

    return [$file, $title];
}

$offset = 0;

while (true) {
    $updates = api("getUpdates", [
        "offset" => $offset,
        "timeout" => 30
    ]);

    if (!isset($updates["result"])) {
        sleep(1);
        continue;
    }

    foreach ($updates["result"] as $update) {
        $offset = $update["update_id"] + 1;

        if (!isset($update["message"])) {
            continue;
        }

        $msg = $update["message"];
        $chat_id = $msg["chat"]["id"];
        $user_id = $msg["from"]["id"];
        $text = $msg["text"] ?? "";

        if ($text == "/start") {
            if (!is_subscribed($user_id)) {
                api("sendMessage", [
                    "chat_id" => $chat_id,
                    "text" => "⚠️ اشترك بالقناة أولاً",
                    "reply_markup" => sub_keyboard()
                ]);
                continue;
            }

            global $START_PHOTO;

            api("sendPhoto", [
                "chat_id" => $chat_id,
                "photo" => $START_PHOTO,
                "caption" => start_text(),
                "reply_markup" => main_keyboard()
            ]);

            continue;
        }

        if (mb_strpos($text, "يوت ") === 0 || mb_strpos($text, "تشغيل ") === 0) {
            if (!is_subscribed($user_id)) {
                api("sendMessage", [
                    "chat_id" => $chat_id,
                    "text" => "⚠️ اشترك بالقناة أولاً",
                    "reply_markup" => sub_keyboard()
                ]);
                continue;
            }

            $query = trim(str_replace(["يوت ", "تشغيل "], "", $text));

            if ($query == "") {
                api("sendMessage", [
                    "chat_id" => $chat_id,
                    "text" => "اكتب اسم الأغنية"
                ]);
                continue;
            }

            $loading = api("sendMessage", [
                "chat_id" => $chat_id,
                "text" => "🔎 جاري البحث..."
            ]);

            try {
                list($file, $title) = download_audio($query);

                api("sendAudio", [
                    "chat_id" => $chat_id,
                    "audio" => new CURLFile(realpath($file)),
                    "title" => $title,
                    "performer" => "Song fadi",
                    "caption" => "🎧 ".$title,
                    "reply_to_message_id" => $msg["message_id"]
                ]);

                if (isset($loading["result"]["message_id"])) {
                    api("deleteMessage", [
                        "chat_id" => $chat_id,
                        "message_id" => $loading["result"]["message_id"]
                    ]);
                }

                @unlink($file);

            } catch (Exception $e) {
                api("sendMessage", [
                    "chat_id" => $chat_id,
                    "text" => "❌ صار خطأ:\n".$e->getMessage()
                ]);
            }
        }
    }
}
?>

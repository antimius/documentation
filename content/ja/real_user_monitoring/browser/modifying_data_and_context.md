---
title: RUM データとコンテキストの変更
kind: documentation
aliases:
  - /ja/real_user_monitoring/installation/advanced_configuration/
  - /ja/real_user_monitoring/browser/advanced_configuration/
further_reading:
  - link: 'https://www.datadoghq.com/blog/real-user-monitoring-with-datadog/'
    tag: ブログ
    text: Real User Monitoring
  - link: /real_user_monitoring/browser/data_collected/
    tag: ドキュメント
    text: 収集された RUM ブラウザデータ
  - link: /real_user_monitoring/explorer/
    tag: ドキュメント
    text: Datadog でビューを検索する
  - link: /real_user_monitoring/explorer/analytics/
    tag: ドキュメント
    text: イベントに関する分析論を組み立てる
  - link: /logs/log_configuration/attributes_naming_convention
    tag: ドキュメント
    text: Datadog 標準属性
---
RUM によって[収集されたデータ][1]を変更して、次のニーズをサポートするには、さまざまな方法があります。

- 個人を特定できる情報などの機密データを保護します。
- サポートを支援するために、ユーザーセッションをそのユーザーの内部 ID に接続します。
- データをサンプリングすることにより、収集する RUM データの量を削減します。
- データの送信元について、デフォルトの属性が提供するものよりも多くのコンテキストを提供します。

## RUM データを強化および制御する

RUM SDK は RUM イベントをキャプチャし、それらの主な属性を設定します。`beforeSend` コールバック関数を使用すると、RUM SDK によって収集されたすべてのイベントにアクセスしてから Datadog に送信できます。RUM イベントをインターセプトすると、次のことが可能になります。

- 追加のコンテキスト属性で RUM イベントを強化する
- RUM イベントを変更して、コンテンツを変更したり、機密性の高いシーケンスを編集したりします ([編集可能なプロパティのリスト](#modify-the-content-of-a-rum-event)を参照してください)
- 選択した RUM イベントを破棄する

[バージョン 2.13.0][2] 以降、`beforeSend` は 2 つの引数を取ります。RUM SDK によって生成された `event` と、RUM イベントの作成をトリガーした `context` です。

```javascript
function beforeSend(event, context)
```

潜在的な `context` 値は次のとおりです。

| RUM イベントタイプ   | コンテキスト                   |
|------------------|---------------------------|
| ビュー             | [場所][3]                  |
| アクション           | [イベント][4]                     |
| リソース (XHR)   | [XMLHttpRequest][5] と [PerformanceResourceTiming][6]            |
| リソース (フェッチ) | [リクエスト][7]、[リソース][8]、[PerformanceResourceTiming][6]      |
| リソース (その他) | [PerformanceResourceTiming][6] |
| エラー            | [エラー][9]                     |
| ロングタスク        | [PerformanceLongTaskTiming][10] |

詳細については、[RUM データの強化と制御ガイド][11]を参照してください。

### RUM イベントを強化する

[グローバルコンテキスト API](#global-context) で追加された属性に加えて、イベントにコンテキスト属性を追加できます。たとえば、フェッチ応答オブジェクトから抽出されたデータで RUM リソースイベントにタグを付けます。

{{< tabs >}}
{{% tab "NPM" %}}

```javascript
import { datadogRum } from '@datadog/browser-rum';

datadogRum.init({
    ...,
    beforeSend: (event, context) => {
        // RUM リソースの応答ヘッダーを収集します
        if (event.type = 'resource' && event.resource.type === 'fetch') {
            event.context = {...event.context, responseHeaders: context.response.headers}
        }
    },
    ...
});
```
{{% /tab %}}
{{% tab "CDN async" %}}
```javascript
DD_RUM.onReady(function() {
    DD_RUM.init({
        ...,
        beforeSend: (event, context) => {
            // RUM リソースの応答ヘッダーを収集します
            if (event.type = 'resource' && event.resource.type === 'fetch') {
                event.context = {...event.context, responseHeaders: context.response.headers}
            }
        },
        ...
    })
})
```
{{% /tab %}}
{{% tab "CDN sync" %}}
```javascript
window.DD_RUM &&
    window.DD_RUM.init({
        ...,
        beforeSend: (event, context) => {
            // RUM リソースの応答ヘッダーを収集します
            if (event.type = 'resource' && event.resource.type === 'fetch') {
                event.context = {...event.context, responseHeaders: context.response.headers}
            }
        },
        ...
    });
```
{{% /tab %}}
{{< /tabs >}}

**注**: RUM SDK は以下を無視します。
- `event.context` の外に追加された属性。
- RUM ビューイベントコンテキストに加えられた変更。

### RUM イベントのコンテンツを変更

たとえば、Web アプリケーションの URL からメールアドレスを編集します。

{{< tabs >}}
{{% tab "NPM" %}}

```javascript
import { datadogRum } from '@datadog/browser-rum';

datadogRum.init({
    ...,
    beforeSend: (event) => {
        // ビューの URL からメールを削除します
        event.view.url = event.view.url.replace(/email=[^&]*/, "email=REDACTED")
    },
    ...
});
```

{{% /tab %}}
{{% tab "CDN async" %}}
```javascript
DD_RUM.onReady(function() {
    DD_RUM.init({
        ...,
        beforeSend: (event) => {
            // ビューの URL からメールを削除します
            event.view.url = event.view.url.replace(/email=[^&]*/, "email=REDACTED")
        },
        ...
    })
})
```
{{% /tab %}}
{{% tab "CDN sync" %}}

```javascript
window.DD_RUM &&
    window.DD_RUM.init({
        ...,
        beforeSend: (event) => {
            // ビューの URL からメールを削除します
            event.view.url = event.view.url.replace(/email=[^&]*/, "email=REDACTED")
        },
        ...
    });
```

{{% /tab %}}
{{< /tabs >}}

次のイベントプロパティを更新できます。

|   属性           |   タイプ    |   説明                                                                                       |
|-----------------------|-----------|-----------------------------------------------------------------------------------------------------|
|   `view.url`            |   文字列  |   アクティブな Web ページの URL。                            |
|   `view.referrer`       |   文字列  |   現在リクエストされているページへのリンクがたどられた前のウェブページの URL。  |
|   `action.target.name`  |   文字列  |   ユーザーが操作した要素。自動的に収集されたアクションの場合のみ。              |
|   `error.message`       |   文字列  |   エラーについて簡潔にわかりやすく説明する 1 行メッセージ。                                 |
|   `error.stack `        |   文字列  |   スタックトレースまたはエラーに関する補足情報。                                     |
|   `error.resource.url`  |   文字列  |   エラーをトリガーしたリソース URL。                                                        |
|   `resource.url`        |   文字列  |   リソースの URL。                                                                                 |
|   `context`        |   オブジェクト  |   [グローバルコンテキスト API](#global-context) を介して、またはイベントを手動で生成するときに追加される属性 (例: `addError` および `addAction`)。RUM ビューイベント `context` は読み取り専用です。                                                                                 |

**注**: RUM SDK は、上記にリストされていないイベントプロパティに加えられた変更を無視します。すべてのイベントプロパティについては、[Browser SDK リポジトリ][12]を参照してください。

### RUM イベントを破棄

`beforeSend` API で、`false` を返し RUM イベントを破棄します。

{{< tabs >}}
{{% tab "NPM" %}}

```javascript
import { datadogRum } from '@datadog/browser-rum';

datadogRum.init({
    ...,
    beforeSend: (event) => {
        if (shouldDiscard(event)) {
            return false
        }
        ...
    },
    ...
});
```

{{% /tab %}}
{{% tab "CDN async" %}}
```javascript
DD_RUM.onReady(function() {
    DD_RUM.init({
        ...,
        beforeSend: (event) => {
            if (shouldDiscard(event)) {
                return false
            },
            ...
        },
        ...
    })
})
```
{{% /tab %}}
{{% tab "CDN sync" %}}

```javascript
window.DD_RUM &&
    window.DD_RUM.init({
        ...,
        beforeSend: (event) => {
            if (shouldDiscard(event)) {
                return false
            }
            ...
        },
        ...
    });
```

{{% /tab %}}
{{< /tabs >}}

## ユーザーセッションを特定する

RUM セッションにユーザー情報を追加すると、次のことが簡単になります。
* 特定のユーザーのジャーニーをたどる
* エラーの影響を最も受けているユーザーを把握する
* 最も重要なユーザーのパフォーマンスを監視する

{{< img src="real_user_monitoring/browser/advanced_configuration/user-api.png" alt="RUM UI のユーザー API"  >}}

次の属性は**オプション**ですが、**少なくとも 1 つ**を指定することをお勧めします。

| 属性  | タイプ | 説明                                                                                              |
|------------|------|----------------------------------------------------------------------------------------------------|
| `usr.id`    | 文字列 | 一意のユーザー識別子。                                                                                  |
| `usr.name`  | 文字列 | RUM UI にデフォルトで表示されるユーザーフレンドリーな名前。                                                  |
| `usr.email` | 文字列 | ユーザー名が存在しない場合に RUM UI に表示されるユーザーのメール。Gravatar をフェッチするためにも使用されます。 |

**注**: 推奨される属性に加えてさらに属性を追加することで、フィルタリング機能を向上できます。たとえば、ユーザープランに関する情報や、所属するユーザーグループなどを追加します。

ユーザーセッションを識別するには、`setUser` API を使用します。

{{< tabs >}}
{{% tab "NPM" %}}
```javascript
datadogRum.setUser({
    id: '1234',
    name: 'John Doe',
    email: 'john@doe.com',
    plan: 'premium',
    ...
})
```

{{% /tab %}}
{{% tab "CDN async" %}}
```javascript
DD_RUM.onReady(function() {
    DD_RUM.setUser({
        id: '1234',
        name: 'John Doe',
        email: 'john@doe.com',
        plan: 'premium',
        ...
    })
})
```
{{% /tab %}}
{{% tab "CDN sync" %}}

```javascript
window.DD_RUM && window.DD_RUM.setUser({
    id: '1234',
    name: 'John Doe',
    email: 'john@doe.com',
    plan: 'premium',
    ...
})
```

{{% /tab %}}
{{< /tabs >}}

### ユーザー ID を削除

`removeUser` API で、以前に設定されたユーザーを消去します。この後に収集されたすべての RUM イベントにユーザー情報は含まれません。

{{< tabs >}}
{{% tab "NPM" %}}
```javascript
datadogRum.removeUser()
```

{{% /tab %}}
{{% tab "CDN async" %}}
```javascript
DD_RUM.onReady(function() {
    DD_RUM.removeUser()
})
```
{{% /tab %}}
{{% tab "CDN sync" %}}

```javascript
window.DD_RUM && window.DD_RUM.removeUser()
```

{{% /tab %}}
{{< /tabs >}}

## サンプリング

デフォルトでは、収集セッション数にサンプリングは適用されていません。収集セッション数に相対サンプリング (% 表示) を適用するには、RUM を初期化する際に `sampleRate` パラメーターを使用します。下記の例では、RUM アプリケーションの全セッションの 90% のみを収集します。

{{< tabs >}}
{{% tab "NPM" %}}

```javascript
import { datadogRum } from '@datadog/browser-rum';

datadogRum.init({
    applicationId: '<DATADOG_APPLICATION_ID>',
    clientToken: '<DATADOG_CLIENT_TOKEN>',
    site: '<DATADOG_SITE>',
    sampleRate: 90,
});
```

{{% /tab %}}
{{% tab "CDN async" %}}
```html
<script>
 (function(h,o,u,n,d) {
   h=h[d]=h[d]||{q:[],onReady:function(c){h.q.push(c)}}
   d=o.createElement(u);d.async=1;d.src=n
   n=o.getElementsByTagName(u)[0];n.parentNode.insertBefore(d,n)
})(window,document,'script','https://www.datadoghq-browser-agent.com/datadog-rum.js','DD_RUM')
  DD_RUM.onReady(function() {
    DD_RUM.init({
        clientToken: '<CLIENT_TOKEN>',
        applicationId: '<APPLICATION_ID>',
        site: '<DATADOG_SITE>',
        sampleRate: 90,
    })
  })
</script>
```
{{% /tab %}}
{{% tab "CDN sync" %}}

```javascript
window.DD_RUM &&
    window.DD_RUM.init({
        clientToken: '<CLIENT_TOKEN>',
        applicationId: '<APPLICATION_ID>',
        site: '<DATADOG_SITE>',
        sampleRate: 90,
    });
```

{{% /tab %}}
{{< /tabs >}}

**注**: サンプルとして抽出したセッションでは、すべてのページビューとそのセッションに紐付くテレメトリーは収集されません。

## グローバルコンテキスト

### グローバルコンテキストを追加

RUM を初期化したら、`addRumGlobalContext(key: string, value: any)` API を使用してアプリケーションから収集したすべての RUM  イベントにコンテキストを追加します。

{{< tabs >}}
{{% tab "NPM" %}}

```javascript
import { datadogRum } from '@datadog/browser-rum';

datadogRum.addRumGlobalContext('<CONTEXT_KEY>', <CONTEXT_VALUE>);

// コード例
datadogRum.addRumGlobalContext('activity', {
    hasPaid: true,
    amount: 23.42
});
```

{{% /tab %}}
{{% tab "CDN async" %}}
```javascript
DD_RUM.onReady(function() {
    DD_RUM.addRumGlobalContext('<CONTEXT_KEY>', '<CONTEXT_VALUE>');
})

// コード例
DD_RUM.onReady(function() {
    DD_RUM.addRumGlobalContext('activity', {
        hasPaid: true,
        amount: 23.42
    });
})
```
{{% /tab %}}
{{% tab "CDN sync" %}}

```javascript
window.DD_RUM && window.DD_RUM.addRumGlobalContext('<CONTEXT_KEY>', '<CONTEXT_VALUE>');

// コード例
window.DD_RUM && window.DD_RUM.addRumGlobalContext('activity', {
    hasPaid: true,
    amount: 23.42
});
```

{{% /tab %}}
{{< /tabs >}}

**注**: 製品全体でデータの相関を高めるには [Datadog の命名規則][13]に従ってください。

### グローバルコンテキストを置換

RUM を初期化したら、`setRumGlobalContext(context: Context)` API を使用してすべての RUM イベントのデフォルトコンテキストを置換します。

{{< tabs >}}
{{% tab "NPM" %}}

```javascript
import { datadogRum } from '@datadog/browser-rum';

datadogRum.setRumGlobalContext({ '<コンテキストキー>', <コンテキスト値>' });

// Code example
datadogRum.setRumGlobalContext({
    codeVersion: 34,
});
```

{{% /tab %}}
{{% tab "CDN async" %}}
```javascript
DD_RUM.onReady(function() {
    DD_RUM.setRumGlobalContext({ '<CONTEXT_KEY>': '<CONTEXT_VALUE>' });
})

// コード例
DD_RUM.onReady(function() {
    DD_RUM.setRumGlobalContext({
        codeVersion: 34,
    })
})
```
{{% /tab %}}
{{% tab "CDN sync" %}}

```javascript
window.DD_RUM &&
    DD_RUM.setRumGlobalContext({ '<コンテキストキー>', <コンテキスト値>' });

// Code example
window.DD_RUM &&
    DD_RUM.setRumGlobalContext({
        codeVersion: 34,
    });
```

{{% /tab %}}
{{< /tabs >}}

**注**: 製品全体でデータの相関を高めるには [Datadog の命名規則][13]に従ってください。

### グローバルコンテキストを読み取る

RUM を初期化したら、`getRumGlobalContext()` API を使用してグローバルコンテキストを読み取ります。

{{< tabs >}}
{{% tab "NPM" %}}

```javascript
import { datadogRum } from '@datadog/browser-rum';

const context = datadogRum.getRumGlobalContext();
```

{{% /tab %}}
{{% tab "CDN async" %}}
```javascript
DD_RUM.onReady(function() {
  var context = DD_RUM.getRumGlobalContext();
});
```
{{% /tab %}}
{{% tab "CDN sync" %}}

```javascript
var context = window.DD_RUM && DD_RUM.getRumGlobalContext();
```

{{% /tab %}}
{{< /tabs >}}



## その他の参考資料

{{< partial name="whats-next/whats-next.html" >}}


[1]: /ja/real_user_monitoring/browser/data_collected/
[2]: https://github.com/DataDog/browser-sdk/blob/main/CHANGELOG.md#v2130
[3]: https://developer.mozilla.org/en-US/docs/Web/API/Location
[4]: https://developer.mozilla.org/en-US/docs/Web/API/Event
[5]: https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest
[6]: https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming
[7]: https://developer.mozilla.org/en-US/docs/Web/API/Request
[8]: https://developer.mozilla.org/en-US/docs/Web/API/Response
[9]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error
[10]: https://developer.mozilla.org/en-US/docs/Web/API/PerformanceLongTaskTiming
[11]: /ja/real_user_monitoring/guide/enrich-and-control-rum-data
[12]: https://github.com/DataDog/browser-sdk/blob/main/packages/rum-core/src/rumEvent.types.ts
[13]: /ja/logs/log_configuration/attributes_naming_convention/#user-related-attributes
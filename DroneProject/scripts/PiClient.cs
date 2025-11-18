using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Text;

public class PiClient : MonoBehaviour
{
    // 👇 Set this in the Inspector to your Pi's address (IP or .local)
    [SerializeField] string piHost = "http://drone.local:5000";

    void Start()
    {
        // Ping once when the scene starts
        StartCoroutine(GetPing());
    }

    // ===== GET: /ping =====
    public IEnumerator GetPing()
    {
        using (UnityWebRequest req = UnityWebRequest.Get($"{piHost}/ping"))
        {
            yield return req.SendWebRequest();

            if (req.result == UnityWebRequest.Result.Success)
                Debug.Log($"[Pi] /ping → {req.downloadHandler.text}");
            else
                Debug.LogError($"[Pi] Ping failed: {req.error}");
        }
    }

    // ===== POST: /toggle =====
    public void ToggleOnPi()
    {
        StartCoroutine(PostJson("/toggle", "{}"));
    }

    // ===== POST: /echo =====
    public void SendEcho()
    {
        string json = "{\"hello\":\"from Unity\"}";
        StartCoroutine(PostJson("/echo", json));
    }

    // ===== Helper coroutine for POST =====
    IEnumerator PostJson(string path, string json)
    {
        byte[] bodyRaw = Encoding.UTF8.GetBytes(json);
        using (UnityWebRequest req = new UnityWebRequest($"{piHost}{path}", "POST"))
        {
            req.uploadHandler = new UploadHandlerRaw(bodyRaw);
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");

            yield return req.SendWebRequest();

            if (req.result == UnityWebRequest.Result.Success)
                Debug.Log($"[Pi] {path} → {req.downloadHandler.text}");
            else
                Debug.LogError($"[Pi] POST {path} failed: {req.error}");
        }
    }
}

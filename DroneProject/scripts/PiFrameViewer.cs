using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using System.Collections;

public class PiFrameViewer : MonoBehaviour
{
    [SerializeField] string piHost = "http://192.168.0.165:5000"; // <-- set to your Pi IP
    [SerializeField] RawImage target;                              // drag your RawImage here
    [SerializeField] float fps = 5f;                               // start low; increase later

    Texture2D current;

    void Start()
    {
        if (!target) target = GetComponentInChildren<RawImage>();
        StartCoroutine(FrameLoop());
    }

    IEnumerator FrameLoop()
    {
        var wait = new WaitForSeconds(1f / Mathf.Max(1f, fps));
        while (true)
        {
            using (var req = UnityWebRequestTexture.GetTexture($"{piHost}/frame.jpg"))
            {
                yield return req.SendWebRequest();

                if (req.result == UnityWebRequest.Result.Success)
                {
                    var tex = DownloadHandlerTexture.GetContent(req);
                    if (current) Destroy(current);
                    current = tex;
                    if (target) target.texture = current;
                }
                else
                {
                    Debug.LogError($"[Pi] frame fetch failed: {req.error}");
                }
            }
            yield return wait;
        }
    }
}

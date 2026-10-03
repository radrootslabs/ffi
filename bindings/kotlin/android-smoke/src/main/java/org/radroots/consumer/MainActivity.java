package org.radroots.consumer;
import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import org.radroots.Radroots;
public class MainActivity extends Activity {
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        for (int i = 0; i < 10000; i++) {
            if (!Radroots.name().equals("Radroots")) throw new AssertionError("name");
        }
        Radroots.printName();
        Log.i("RadrootsConsumer", "RADROOTS_CONSUMER_OK");
        finish();
    }
}

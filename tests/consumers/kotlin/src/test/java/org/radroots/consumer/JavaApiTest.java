package org.radroots.consumer;

import org.radroots.Radroots;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class JavaApiTest {
    @Test
    void publicStaticFacade() throws ReflectiveOperationException {
        assertEquals("Radroots", Radroots.NAME);
        assertEquals("Radroots", Radroots.name());
        assertEquals(String.class, Radroots.class.getMethod("name").getReturnType());
        assertEquals(void.class, Radroots.class.getMethod("printName").getReturnType());
        for (Method method : Radroots.class.getDeclaredMethods()) {
            if (Modifier.isPublic(method.getModifiers())) {
                assertTrue(Modifier.isStatic(method.getModifiers()));
                assertFalse(method.getReturnType().getName().startsWith("com.sun.jna."));
                for (Class<?> parameter : method.getParameterTypes()) {
                    assertFalse(parameter.getName().startsWith("com.sun.jna."));
                }
            }
        }
    }
}
